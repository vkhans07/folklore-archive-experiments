# Thailand: v3 source and output evidence

This bundle reproduces supplied OCR and saved outputs. Source PDF pixels were not reviewed. Token differences are diagnostics, not error counts: header removal and whitespace changes may be intended.

[Original PDF](</Users/vkhans/Desktop/folklore-archive-experiments/JSONs/Thailand Folkspeech.pdf>) | [Prepared input](</Users/vkhans/Desktop/folklore-archive-experiments/outputs/inputs/00002_56_Thailand_Folkspeech__38.json>)

## Source OCR (one-based page numbers)

### Page 1

Aaland “Fore sfeecn Folk Speech — Thai Myself, Age 21. Female Student, Library Assistant, Admin. Assistant ‘Thai and 4" generation Chinese in Thailand English, Central Thai Bellflower, CA.; November 8, 2002 mutual aly ony /3u/#/ as tus 14 sam/wan/dee/ see / wan / khai/ three /day /good/ —_four/ day / fever/ Good for three days and fevered for four days. This is a description I learned from my father, Boonlert Nakkeow. He used this to describe my relationship with my 2000-2001 roommate at Stern Hall, the all-female dormitory at UC Berkeley. She was prone to extreme moodswings. One day should she would be laughing and smiling and the next she would be really terse and quiet. This bit of folk speech is a personality description used to describe a person with rapidly changing moods who also does not pause to explain why either. Varinthorn Nakkeow, Age 21. 10420 Trabuco St.; Bellflower, CA 90706

## sonnet

[Raw response](</Users/vkhans/Desktop/folklore-archive-experiments/outputs/runs/archive/development/sonnet/00002_56_Thailand_Folkspeech__38/67422c563125524735b2fe99f549033c0ec35e1d2ee7091b8bd47d062c63b4cf/response.txt>) | [Archive JSON](</Users/vkhans/Desktop/folklore-archive-experiments/outputs/runs/archive/development/sonnet/00002_56_Thailand_Folkspeech__38/67422c563125524735b2fe99f549033c0ec35e1d2ee7091b8bd47d062c63b4cf/archive.json>) | [Run record](</Users/vkhans/Desktop/folklore-archive-experiments/outputs/runs/archive/development/sonnet/00002_56_Thailand_Folkspeech__38/67422c563125524735b2fe99f549033c0ec35e1d2ee7091b8bd47d062c63b4cf/run.json>)

Latency: 6.609 seconds; attempts: 1; schema valid: True.

### Structured fields

```json
{
  "_id": null,
  "analysis": {
    "collector_comments": null,
    "context": {
      "collection_context": "This is a description I learned from my father, Boonlert Nakkeow.",
      "cultural_background": null,
      "use_context": "He used this to describe my relationship with my 2000-2001 roommate at Stern Hall, the all-female dormitory at UC Berkeley. This bit of folk speech is a personality description used to describe a person with rapidly changing moods who also does not pause to explain why either."
    },
    "interpretation": "She was prone to extreme moodswings. One day should she would be laughing and smiling and the next she would be really terse and quiet."
  },
  "collector": {
    "collector_comments": "Collector attribution is uncertain: the signature block at the bottom (Varinthorn Nakkeow, Age 21) is presumed to identify the collector, who also appears to be the first-person informant 'Myself'. The contributor's name is not given separately; the contributor details come from the 'Myself, Age 21. Female' header, and the contributor and collector may be the same person. The first line of the item and the single word 'mutual aly' are garbled OCR.",
    "gender": null,
    "name": "Varinthorn Nakkeow"
  },
  "contributor": {
    "age_bucket": "18-24",
    "ethnicity": "Thai and 4th generation Chinese in Thailand",
    "gender": "Female",
    "languages_spoken": [
      "English",
      "Central Thai"
    ],
    "name": null,
    "nationality": null,
    "occupation": "Student, Library Assistant, Admin. Assistant"
  },
  "date_collected": "November 8, 2002",
  "filename": "JSONs/Thailand Folkspeech.pdf",
  "folklore": {
    "item": "ony /3u/#/ as tus 14\nsam/wan/dee/ see / wan / khai/\nthree /day /good/ —_four/ day / fever/",
    "medium": null,
    "place_mentioned": [],
    "translation": "Good for three days and fevered for four days."
  },
  "location_collected": {
    "city": "Bellflower",
    "country": null,
    "geolocation": null,
    "state": "CA"
  },
  "storage_medium": "PDF"
}
```

### cleaned_full_text

Aaland “Fore sfeecn Folk Speech — Thai Myself, Age 21. Female Student, Library Assistant, Admin. Assistant ‘Thai and 4" generation Chinese in Thailand English, Central Thai Bellflower, CA.; November 8, 2002 mutual aly ony /3u/#/ as tus 14 sam/wan/dee/ see / wan / khai/ three /day /good/ —_four/ day / fever/ Good for three days and fevered for four days. This is a description I learned from my father, Boonlert Nakkeow. He used this to describe my relationship with my 2000-2001 roommate at Stern Hall, the all-female dormitory at UC Berkeley. She was prone to extreme moodswings. One day should she would be laughing and smiling and the next she would be really terse and quiet. This bit of folk speech is a personality description used to describe a person with rapidly changing moods who also does not pause to explain why either. Varinthorn Nakkeow, Age 21. 10420 Trabuco St.; Bellflower, CA 90706

### Changes from supplied OCR

No differences after splitting on whitespace: the full OCR was retained.


## haiku

[Raw response](</Users/vkhans/Desktop/folklore-archive-experiments/outputs/runs/archive/development/haiku/00002_56_Thailand_Folkspeech__38/60cc6d84ae732bcf363433242a710b7438c7c139eb198a661785055ad370b957/response.txt>) | [Archive JSON](</Users/vkhans/Desktop/folklore-archive-experiments/outputs/runs/archive/development/haiku/00002_56_Thailand_Folkspeech__38/60cc6d84ae732bcf363433242a710b7438c7c139eb198a661785055ad370b957/archive.json>) | [Run record](</Users/vkhans/Desktop/folklore-archive-experiments/outputs/runs/archive/development/haiku/00002_56_Thailand_Folkspeech__38/60cc6d84ae732bcf363433242a710b7438c7c139eb198a661785055ad370b957/run.json>)

Latency: 23.648 seconds; attempts: 1; schema valid: True.

### Structured fields

```json
{
  "_id": null,
  "analysis": {
    "collector_comments": null,
    "context": {
      "collection_context": "This is a description I learned from my father, Boonlert Nakkeow.",
      "cultural_background": null,
      "use_context": "He used this to describe my relationship with my 2000-2001 roommate at Stern Hall, the all-female dormitory at UC Berkeley. She was prone to extreme moodswings. One day should she would be laughing and smiling and the next she would be really terse and quiet."
    },
    "interpretation": "This bit of folk speech is a personality description used to describe a person with rapidly changing moods who also does not pause to explain why either."
  },
  "collector": {
    "collector_comments": "The collector is not named in the source. The account appears to be a first-person form completed by the contributor, so attribution of collection to the contributor is uncertain. The Bellflower, CA address in the contributor block was not used as the collection location.",
    "gender": null,
    "name": null
  },
  "contributor": {
    "age_bucket": "18-24",
    "ethnicity": "‘Thai and 4\" generation Chinese in Thailand",
    "gender": "female",
    "languages_spoken": [
      "English",
      "Central Thai"
    ],
    "name": "Varinthorn Nakkeow",
    "nationality": null,
    "occupation": "Student, Library Assistant, Admin. Assistant"
  },
  "date_collected": "November 8, 2002",
  "filename": "JSONs/Thailand Folkspeech.pdf",
  "folklore": {
    "item": "ony /3u/#/ as tus 14\nsam/wan/dee/ see / wan / khai/",
    "medium": "oral",
    "place_mentioned": [],
    "translation": "three /day /good/ —_four/ day / fever/\nGood for three days and fevered for four days."
  },
  "location_collected": {
    "city": null,
    "country": null,
    "geolocation": null,
    "state": null
  },
  "storage_medium": "PDF"
}
```

### cleaned_full_text

Myself, Age 21. Female Student, Library Assistant, Admin. Assistant ‘Thai and 4" generation Chinese in Thailand English, Central Thai Bellflower, CA.; November 8, 2002 mutual aly ony /3u/#/ as tus 14 sam/wan/dee/ see / wan / khai/ three /day /good/ —_four/ day / fever/ Good for three days and fevered for four days. This is a description I learned from my father, Boonlert Nakkeow. He used this to describe my relationship with my 2000-2001 roommate at Stern Hall, the all-female dormitory at UC Berkeley. She was prone to extreme moodswings. One day should she would be laughing and smiling and the next she would be really terse and quiet. This bit of folk speech is a personality description used to describe a person with rapidly changing moods who also does not pause to explain why either. Varinthorn Nakkeow, Age 21. 10420 Trabuco St.; Bellflower, CA 90706

### Changes from supplied OCR

- delete: `Aaland “Fore sfeecn Folk Speech — Thai` → ``

## gemini_flash

[Raw response](</Users/vkhans/Desktop/folklore-archive-experiments/outputs/runs/archive/development/gemini_flash/00002_56_Thailand_Folkspeech__38/05aa918d5beeefaadd3d3a5d6fa259f586eea6581fbc2c4f96b43871051f0c46/response.txt>) | [Archive JSON](</Users/vkhans/Desktop/folklore-archive-experiments/outputs/runs/archive/development/gemini_flash/00002_56_Thailand_Folkspeech__38/05aa918d5beeefaadd3d3a5d6fa259f586eea6581fbc2c4f96b43871051f0c46/archive.json>) | [Run record](</Users/vkhans/Desktop/folklore-archive-experiments/outputs/runs/archive/development/gemini_flash/00002_56_Thailand_Folkspeech__38/05aa918d5beeefaadd3d3a5d6fa259f586eea6581fbc2c4f96b43871051f0c46/run.json>)

Latency: 59.009 seconds; attempts: 1; schema valid: True.

### Structured fields

```json
{
  "_id": null,
  "analysis": {
    "collector_comments": null,
    "context": {
      "collection_context": "This is a description I learned from my father, Boonlert Nakkeow.",
      "cultural_background": null,
      "use_context": "He used this to describe my relationship with my 2000-2001 roommate at Stern Hall, the all-female dormitory at UC Berkeley. She was prone to extreme moodswings. One day should she would be laughing and smiling and the next she would be really terse and quiet."
    },
    "interpretation": "This bit of folk speech is a personality description used to describe a person with rapidly changing moods who also does not pause to explain why either."
  },
  "collector": {
    "collector_comments": "The collector appears to be the informant ('Myself', Varinthorn Nakkeow).",
    "gender": "Female",
    "name": "Varinthorn Nakkeow"
  },
  "contributor": {
    "age_bucket": "18-24",
    "ethnicity": "‘Thai and 4\" generation Chinese in Thailand",
    "gender": "Female",
    "languages_spoken": [
      "English",
      "Central Thai"
    ],
    "name": "Varinthorn Nakkeow",
    "nationality": null,
    "occupation": "Student, Library Assistant, Admin. Assistant"
  },
  "date_collected": "November 8, 2002",
  "filename": "JSONs/Thailand Folkspeech.pdf",
  "folklore": {
    "item": "mutual aly\nony /3u/#/ as tus 14\nsam/wan/dee/ see / wan / khai/",
    "medium": null,
    "place_mentioned": [],
    "translation": "three /day /good/ —_four/ day / fever/\nGood for three days and fevered for four days."
  },
  "location_collected": {
    "city": "Bellflower",
    "country": null,
    "geolocation": null,
    "state": "CA"
  },
  "storage_medium": "PDF"
}
```

### cleaned_full_text

Folk Speech — Thai
Myself, Age 21. Female
Student, Library Assistant, Admin. Assistant
‘Thai and 4" generation Chinese in Thailand
English, Central Thai
Bellflower, CA.; November 8, 2002
mutual aly
ony /3u/#/
as tus
14
sam/wan/dee/ see / wan / khai/
three /day /good/ —_four/ day / fever/
Good for three days and fevered for four days.
This is a description I learned from my father, Boonlert Nakkeow. He used this to describe my relationship with my 2000-2001 roommate at Stern Hall, the all-female dormitory at UC Berkeley. She was prone to extreme moodswings. One day should she would be laughing and smiling and the next she would be really terse and quiet. This bit of folk speech is a personality description used to describe a person with rapidly changing moods who also does not pause to explain why either.
Varinthorn Nakkeow, Age 21.
10420 Trabuco St.; Bellflower, CA 90706

### Changes from supplied OCR

- delete: `Aaland “Fore sfeecn` → ``

## gemini_flash_high

[Raw response](</Users/vkhans/Desktop/folklore-archive-experiments/outputs/runs/archive/development/gemini_flash_high/00002_56_Thailand_Folkspeech__38/f8177ae04710eba0c6a8ff0c8c50cb8a030ef5d6d65fef0fc962e3e494e84fe8/response.txt>) | [Archive JSON](</Users/vkhans/Desktop/folklore-archive-experiments/outputs/runs/archive/development/gemini_flash_high/00002_56_Thailand_Folkspeech__38/f8177ae04710eba0c6a8ff0c8c50cb8a030ef5d6d65fef0fc962e3e494e84fe8/archive.json>) | [Run record](</Users/vkhans/Desktop/folklore-archive-experiments/outputs/runs/archive/development/gemini_flash_high/00002_56_Thailand_Folkspeech__38/f8177ae04710eba0c6a8ff0c8c50cb8a030ef5d6d65fef0fc962e3e494e84fe8/run.json>)

Latency: 281.548 seconds; attempts: 1; schema valid: True.

### Structured fields

```json
{
  "_id": null,
  "analysis": {
    "collector_comments": "Suspect OCR 'mutual aly' precedes 'ony /3u/#/ as tus 14' and may represent a heading or Thai script ('สำนวนไทย', Thai idiom). The folklore item includes the Thai script and transliteration 'sam/wan/dee/ see / wan / khai/'.",
    "context": {
      "collection_context": "This is a description I learned from my father, Boonlert Nakkeow.",
      "cultural_background": null,
      "use_context": "He used this to describe my relationship with my 2000-2001 roommate at Stern Hall, the all-female dormitory at UC Berkeley. She was prone to extreme moodswings. One day should she would be laughing and smiling and the next she would be really terse and quiet."
    },
    "interpretation": "This bit of folk speech is a personality description used to describe a person with rapidly changing moods who also does not pause to explain why either."
  },
  "collector": {
    "collector_comments": "The contributor is identified as 'Myself' (collector Varinthorn Nakkeow). The item was learned from her father, Boonlert Nakkeow.",
    "gender": "Female",
    "name": "Varinthorn Nakkeow"
  },
  "contributor": {
    "age_bucket": "18-24",
    "ethnicity": "‘Thai and 4\" generation Chinese in Thailand",
    "gender": "Female",
    "languages_spoken": [
      "English",
      "Central Thai"
    ],
    "name": "Varinthorn Nakkeow",
    "nationality": null,
    "occupation": "Student, Library Assistant, Admin. Assistant"
  },
  "date_collected": "November 8, 2002",
  "filename": "JSONs/Thailand Folkspeech.pdf",
  "folklore": {
    "item": "mutual aly\nony /3u/#/ as tus 14\nsam/wan/dee/ see / wan / khai/",
    "medium": null,
    "place_mentioned": [],
    "translation": "three /day /good/ —_four/ day / fever/\nGood for three days and fevered for four days."
  },
  "location_collected": {
    "city": "Bellflower",
    "country": null,
    "geolocation": null,
    "state": "CA"
  },
  "storage_medium": "PDF"
}
```

### cleaned_full_text

Folk Speech — Thai Myself, Age 21. Female Student, Library Assistant, Admin. Assistant ‘Thai and 4" generation Chinese in Thailand English, Central Thai Bellflower, CA.; November 8, 2002 mutual aly ony /3u/#/ as tus 14 sam/wan/dee/ see / wan / khai/ three /day /good/ —_four/ day / fever/ Good for three days and fevered for four days. This is a description I learned from my father, Boonlert Nakkeow. He used this to describe my relationship with my 2000-2001 roommate at Stern Hall, the all-female dormitory at UC Berkeley. She was prone to extreme moodswings. One day should she would be laughing and smiling and the next she would be really terse and quiet. This bit of folk speech is a personality description used to describe a person with rapidly changing moods who also does not pause to explain why either. Varinthorn Nakkeow, Age 21. 10420 Trabuco St.; Bellflower, CA 90706

### Changes from supplied OCR

- delete: `Aaland “Fore sfeecn` → ``
