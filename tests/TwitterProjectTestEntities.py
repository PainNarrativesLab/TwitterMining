"""
This holds entities like sample tweets which are used throughout the testsuite
"""
test_tweet = {
"_id": "401352093598253056",
"_rev": "2-64861d45d1696f848786975706ad3bf9",
"truncated": 'false',
"text": u"I might have vulvodynia. Reminds me of Charlotte #satc #sexology #vulvodynia @ Ganzenplein http://t.co/C1E4pgiu2T",
"in_reply_to_status_id": 'null',
"id": 401352093598253060,
"favorite_count": 0,
"source": "<a href=\"http://instagram.com\" rel=\"nofollow\">Instagram</a>",
"retweeted": 'false',
"entities": {
"symbols": [],
"user_mentions": [],
"hashtags": [
    {
    "indices": [56, 61],
    "text": "satc"
    },
    {
    "indices": [62, 71],
    "text": "sexology"
    },
    {
    "indices": [72, 83],
    "text": "vulvodynia"
    }
],
"urls": [
    {
    "url": "http://t.co/C1E4pgiu2T",
    "indices": [98, 120],
    "expanded_url": "http://instagram.com/p/gvPYnCDEPm/",
    "display_url": "instagram.com/p/gvPYnCDEPm/"
    }
]
},
"in_reply_to_screen_name": 'null',
"in_reply_to_user_id": 'null',
"retweet_count": 0,
"id_str": "401352093598253056",
"favorited": 'false',
"user": {
"id": 319297935,
"verified": 'false',
"entities": {
"url": {
"urls": [
    {
    "url": "http://t.co/845k6L9q1k",
    "indices": [0, 22],
    "expanded_url": "http://www.facebook.com/niels.jacobus",
    "display_url": "facebook.com/niels.jacobus"
    }
]
},
"description": {"urls": []}
},
"followers_count": 69,
"id_str": "319297935",
"utc_offset": 7200,
"statuses_count": 137,
"description": "Student seksuologie @KU_Leuven | KSA",
"friends_count": 81,
"location": "Leuven",
"screen_name": "NielsJacobus",
"lang": "en",
"profile_background_tile": 'false',
"favourites_count": 19,
"name": "Niels ",
"url": "http://t.co/845k6L9q1k",
"created_at": "Fri Jun 17 21:54:43 +0000 2011",
"time_zone": "Athens"
},
"lang": "de",
"created_at": "Fri Nov 15 14:12:50 +0000 2013",
"place": 'null',
"metadata": {
"iso_language_code": "de",
"result_type": "recent"
}
}

EXPECTED_TAGS = ['satc', 'sexology', 'vulvodynia']

EXPECTED_TEXT = "I might have vulvodynia. Reminds me of Charlotte #satc #sexology #vulvodynia @ Ganzenplein http://t.co/C1E4pgiu2T"

"""The portion of the tweet object that will be used in saving user """
USER_DICT = {"user": {
"id": 319297935,
"verified": 'false',
"entities": {
"url": {
"urls": [
    {
    "url": "http://t.co/845k6L9q1k",
    "indices": [0, 22],
    "expanded_url": "http://www.facebook.com/niels.jacobus",
    "display_url": "facebook.com/niels.jacobus"
    }
]
},
"description": {"urls": []}
},
"followers_count": 69,
"id_str": "319297935",
"utc_offset": 7200,
"statuses_count": 137,
"description": "Student seksuologie @KU_Leuven | KSA",
"friends_count": 81,
"location": "Leuven",
"screen_name": "NielsJacobus",
"lang": "en",
"profile_background_tile": 'false',
"favourites_count": 19,
"name": "Niels ",
"url": "http://t.co/845k6L9q1k",
"created_at": "Fri Jun 17 21:54:43 +0000 2011",
"time_zone": "Athens"
}}

""" Has the html items """
test_tweet2 = {"_id": "401352093598253056",
               "_rev": "2-64861d45d1696f848786975706ad3bf9",
               "truncated": 'false',
               "text": "\"I might have vulvodynia\". Reminds me of Charlotte 😷💔📺💊 #satc #sexology #vulvodynia @ Ganzenplein http://t.co/C1E4pgiu2T",
               "in_reply_to_status_id": 'null',
               "id": 401352093598253060,
               "favorite_count": 0,
               "source": "<a href=\"http://instagram.com\" rel=\"nofollow\">Instagram</a>",
               "retweeted": 'false',

               "entities": {
                   "symbols": [
                   ],
                   "user_mentions": [
                   ],
                   "hashtags": [
                       {
                           "indices": [
                               56,
                               61
                           ],
                           "text": "satc"
                       },
                       {
                           "indices": [
                               62,
                               71
                           ],
                           "text": "sexology"
                       },
                       {
                           "indices": [
                               72,
                               83
                           ],
                           "text": "vulvodynia"
                       }
                   ],
                   "urls": [
                       {
                           "url": "http://t.co/C1E4pgiu2T",
                           "indices": [
                               98,
                               120
                           ],
                           "expanded_url": "http://instagram.com/p/gvPYnCDEPm/",
                           "display_url": "instagram.com/p/gvPYnCDEPm/"
                       }
                   ]
               },
               "in_reply_to_screen_name": 'null',
               "in_reply_to_user_id": 'null',
               "retweet_count": 0,
               "id_str": "401352093598253056",
               "favorited": 'false',
               "user": {

                   "id": 319297935,
                   "verified": 'false',
                   "entities": {
                       "url": {
                           "urls": [
                               {
                                   "url": "http://t.co/845k6L9q1k",
                                   "indices": [
                                       0,
                                       22
                                   ],
                                   "expanded_url": "http://www.facebook.com/niels.jacobus",
                                   "display_url": "facebook.com/niels.jacobus"
                               }
                           ]
                       },
                       "description": {
                           "urls": [
                           ]
                       }
                   },
                   "followers_count": 69,

                   "id_str": "319297935",

                   "utc_offset": 7200,
                   "statuses_count": 137,
                   "description": "Student seksuologie @KU_Leuven | KSA",
                   "friends_count": 81,
                   "location": "Leuven",
                   "screen_name": "NielsJacobus",
                   "lang": "en",
                   "profile_background_tile": 'false',
                   "favourites_count": 19,
                   "name": "Niels ☕",
                   "url": "http://t.co/845k6L9q1k",
                   "created_at": "Fri Jun 17 21:54:43 +0000 2011",
                   "time_zone": "Athens",
               },

               "lang": "de",
               "created_at": "Fri Nov 15 14:12:50 +0000 2013",

               "place": 'null',
               "metadata": {
                   "iso_language_code": "de",
                   "result_type": "recent"
               }
}