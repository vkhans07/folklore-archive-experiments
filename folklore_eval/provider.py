"""Provider adapters. Vertex uses ADC; direct Anthropic uses ANTHROPIC_API_KEY."""
import time
import json
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


def _error_details(exc, provider="anthropic_vertex"):
    """Return useful provider diagnostics without dumping request credentials/content."""
    status = getattr(exc, "status_code", None) or getattr(exc, "code", None)
    response = getattr(exc, "response", None)
    if status is None and response is not None:
        status = getattr(response, "status_code", None)
    body = getattr(exc, "body", None)
    if body is None and response is not None:
        try:
            body = response.json()
        except Exception:
            body = None
    if not isinstance(body, (dict, list, str, int, float, bool, type(None))):
        body = str(body)
    request_id = getattr(exc, "request_id", None)
    if request_id is None and response is not None:
        headers = getattr(response, "headers", {}) or {}
        request_id = headers.get("request-id") or headers.get("x-request-id")
    message = str(exc)
    body_text = str(body or "")
    combined = (message + " " + body_text).lower()
    if status == 429 and ("quota" in combined or "resource_exhausted" in combined):
        category = "quota_or_capacity"
        next_step = "Check the provider's quota for this model and endpoint."
    elif status in (401, 403) or "permission_denied" in combined or "unauthenticated" in combined:
        category = "authentication_or_permission"
        if provider == "anthropic_direct":
            next_step = "Check the Anthropic API key and Claude Console access."
        elif provider == "gemini_api":
            next_step = "Check the Gemini API key, AI Studio project, billing status, and API access."
        else:
            next_step = "Check local ADC identity, project IAM prediction access, API enablement, and model access."
    elif status == 404 or "not found" in combined or "unsupported location" in combined:
        category = "model_or_location"
        if provider == "anthropic_direct":
            next_step = "Verify the model ID is available to your Anthropic organization."
        elif provider == "gemini_api":
            next_step = "Verify the model ID is available through the Gemini API."
        else:
            next_step = "Verify the model ID is enabled and supported in the configured Google Cloud location."
    elif status == 400 or "invalid_argument" in combined:
        category = "invalid_request"
        next_step = "Inspect the saved request and model documentation for unsupported parameters or request shape."
    elif status is not None and status >= 500:
        category = "provider_service"
        next_step = "Check Google Cloud service health and retry later."
    elif type(exc).__name__ in ("APIConnectionError", "APITimeoutError", "ConnectError", "ReadTimeout"):
        category = "network_or_timeout"
        next_step = "Check network access and timeout settings, then retry."
    else:
        category = "provider_error"
        next_step = "Use the error type, status, and provider message below to investigate the request."
    return {
        "type": type(exc).__name__, "message": message, "status_code": status,
        "provider_request_id": request_id, "provider_body": body,
        "category": category, "next_step": next_step,
    }


def _provider_retry_delay(body, fallback):
    """Honor a provider's retry hint when it supplies one."""
    details = (body.get("error") or {}).get("details", []) if isinstance(body, dict) else []
    for detail in details:
        delay = detail.get("retryDelay", "")
        match = re.fullmatch(r"([0-9.]+)s", str(delay))
        if match:
            return max(fallback, float(match.group(1)))
    message = ((body.get("error") or {}).get("message", "") if isinstance(body, dict) else "")
    match = re.search(r"retry in ([0-9.]+)s", message, re.IGNORECASE)
    return max(fallback, float(match.group(1))) if match else fallback


def request_vertex(project_id, location, request, transport):
    from anthropic import AnthropicVertex, APIConnectionError, APITimeoutError, RateLimitError, InternalServerError

    transient = (APIConnectionError, APITimeoutError, RateLimitError, InternalServerError)
    started = time.monotonic()
    for attempt in range(1, transport["max_attempts"] + 1):
        client = None
        try:
            if client is None:
                client = AnthropicVertex(project_id=project_id, region=location, timeout=transport["timeout_seconds"], max_retries=0)
            response = client.messages.create(**request)
            return response.model_dump(mode="json"), round(time.monotonic() - started, 3), None, attempt
        except transient as exc:
            if attempt == transport["max_attempts"]:
                error = _error_details(exc)
                error["transient"] = True
                return None, round(time.monotonic() - started, 3), error, attempt
            time.sleep(transport["initial_backoff_seconds"] * (2 ** (attempt - 1)))
        except Exception as exc:
            error = _error_details(exc)
            error["transient"] = False
            return None, round(time.monotonic() - started, 3), error, attempt


def request_anthropic_direct(request, transport):
    import os
    from anthropic import Anthropic, APIConnectionError, APITimeoutError, RateLimitError, InternalServerError

    transient = (APIConnectionError, APITimeoutError, RateLimitError, InternalServerError)
    started = time.monotonic()
    client = None
    for attempt in range(1, transport["max_attempts"] + 1):
        try:
            if client is None:
                workspace_id = os.getenv("ANTHROPIC_WORKSPACE_ID")
                headers = {"anthropic-workspace-id": workspace_id} if workspace_id else None
                client = Anthropic(timeout=transport["timeout_seconds"], max_retries=0, default_headers=headers)
            response = client.messages.create(**request)
            return response.model_dump(mode="json"), round(time.monotonic() - started, 3), None, attempt
        except transient as exc:
            if attempt == transport["max_attempts"]:
                error = _error_details(exc, provider="anthropic_direct")
                error["transient"] = True
                return None, round(time.monotonic() - started, 3), error, attempt
            time.sleep(transport["initial_backoff_seconds"] * (2 ** (attempt - 1)))
        except Exception as exc:
            error = _error_details(exc, provider="anthropic_direct")
            error["transient"] = False
            return None, round(time.monotonic() - started, 3), error, attempt


def request_gemini_vertex(project_id, location, request, transport):
    from google import genai
    from google.genai import types

    started = time.monotonic()
    for attempt in range(1, transport["max_attempts"] + 1):
        client = None
        try:
            client = genai.Client(vertexai=True, project=project_id, location=location,
                                  http_options=types.HttpOptions(timeout=int(transport["timeout_seconds"] * 1000)))
            response = client.models.generate_content(
                model=request["model"], contents=request["messages"][0]["content"],
                config=types.GenerateContentConfig(
                    system_instruction=request["system"],
                    max_output_tokens=request["max_tokens"],
                    temperature=request["temperature"],
                    response_mime_type="application/json",
                ),
            )
            payload = response.model_dump(mode="json", exclude_none=True)
            candidates = payload.get("candidates") or []
            candidate = candidates[0] if candidates else {}
            parts = (candidate.get("content") or {}).get("parts") or []
            finish = str(candidate.get("finish_reason") or candidate.get("finishReason") or "").lower()
            usage = payload.get("usage_metadata") or payload.get("usageMetadata") or {}
            normalized = {
                "model": payload.get("model_version") or payload.get("modelVersion") or request["model"],
                "content": [{"type": "text", "text": part["text"]} for part in parts if "text" in part],
                "stop_reason": "max_tokens" if finish == "max_tokens" else finish,
                "usage": {"input_tokens": usage.get("prompt_token_count", usage.get("promptTokenCount")),
                          "output_tokens": usage.get("candidates_token_count", usage.get("candidatesTokenCount"))},
                "provider_response": payload,
            }
            return normalized, round(time.monotonic() - started, 3), None, attempt
        except Exception as exc:
            error = _error_details(exc, provider="gemini_vertex")
            status = error.get("status_code")
            transient = status in (408, 429, 500, 502, 503, 504) or type(exc).__name__ in ("APIConnectionError", "APITimeoutError", "ConnectError", "ReadTimeout")
            if transient and attempt < transport["max_attempts"]:
                time.sleep(transport["initial_backoff_seconds"] * (2 ** (attempt - 1)))
                continue
            error["transient"] = transient
            return None, round(time.monotonic() - started, 3), error, attempt
        finally:
            if client is not None:
                client.close()


def request_gemini_api(request, transport):
    """Call Gemini's GenerateContent API with a Developer API key."""
    import os

    class ProviderHttpError(Exception):
        def __init__(self, status_code, body, request_id=None):
            self.status_code = status_code
            self.body = body
            self.request_id = request_id
            super().__init__(str(body))

    started = time.monotonic()
    for attempt in range(1, transport["max_attempts"] + 1):
        print("Gemini %s: attempt %s/%s starting" % (request["model"], attempt, transport["max_attempts"]), file=sys.stderr, flush=True)
        try:
            api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            endpoint = "https://generativelanguage.googleapis.com/v1beta/models/%s:generateContent" % quote(request["model"], safe="-._")
            body = {
                "systemInstruction": {"parts": [{"text": request["system"]}]},
                "contents": [{"role": "user", "parts": [{"text": request["messages"][0]["content"]}]}],
                "generationConfig": {
                    "maxOutputTokens": request["max_tokens"],
                    "responseMimeType": "application/json",
                    "thinkingConfig": {"thinkingLevel": request.get("thinking_level", "medium")},
                },
            }
            http_request = Request(
                endpoint, data=json.dumps(body).encode("utf-8"),
                headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
                method="POST",
            )
            with urlopen(http_request, timeout=transport["timeout_seconds"]) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            try:
                body = json.loads(exc.read().decode("utf-8"))
            except Exception:
                body = {"message": str(exc)}
            error = _error_details(ProviderHttpError(exc.code, body, exc.headers.get("x-request-id")), provider="gemini_api")
            status = error.get("status_code")
            transient = status in (408, 429, 500, 502, 503, 504)
            if transient and attempt < transport["max_attempts"]:
                fallback = transport["initial_backoff_seconds"] * (2 ** (attempt - 1))
                delay = _provider_retry_delay(body, fallback)
                if delay > transport.get("max_retry_delay_seconds", 300):
                    error.update({"transient": True, "retry_deferred": True, "retry_after_seconds": delay,
                                  "next_step": "Provider requests a wait of %.1fs; defer this request until then instead of blocking the run." % delay})
                    print("Gemini: HTTP %s; provider requests %.1fs wait, deferring request" % (status, delay), file=sys.stderr, flush=True)
                    return None, round(time.monotonic() - started, 3), error, attempt
                print("Gemini: HTTP %s; retrying in %.1fs" % (status, delay), file=sys.stderr, flush=True)
                time.sleep(delay)
                continue
            error["transient"] = transient
            return None, round(time.monotonic() - started, 3), error, attempt
        except (URLError, TimeoutError, OSError) as exc:
            error = _error_details(exc, provider="gemini_api")
            error["transient"] = True
            if attempt < transport["max_attempts"]:
                delay = transport["initial_backoff_seconds"] * (2 ** (attempt - 1))
                print("Gemini: %s; retrying in %.1fs" % (type(exc).__name__, delay), file=sys.stderr, flush=True)
                time.sleep(delay)
                continue
            return None, round(time.monotonic() - started, 3), error, attempt
        try:
            candidates = payload.get("candidates") or []
            candidate = candidates[0] if candidates else {}
            parts = (candidate.get("content") or {}).get("parts") or []
            finish = str(candidate.get("finish_reason") or candidate.get("finishReason") or "").lower()
            usage = payload.get("usage_metadata") or payload.get("usageMetadata") or {}
            normalized = {
                "model": payload.get("model_version") or payload.get("modelVersion") or request["model"],
                "content": [{"type": "text", "text": part["text"]} for part in parts if "text" in part],
                "stop_reason": "max_tokens" if finish == "max_tokens" else finish,
                "usage": {"input_tokens": usage.get("prompt_token_count", usage.get("promptTokenCount")),
                          "output_tokens": usage.get("candidates_token_count", usage.get("candidatesTokenCount"))},
                "provider_response": payload,
            }
            return normalized, round(time.monotonic() - started, 3), None, attempt
        except Exception as exc:
            error = _error_details(exc, provider="gemini_api")
            error["transient"] = False
            return None, round(time.monotonic() - started, 3), error, attempt
