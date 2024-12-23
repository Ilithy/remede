### Table of Contents

- [Introduction](##Introduction)
- [Compliance with data regulations](##compliance-with-data-regulations)
- [Third party cloud service dependencies](##third-party-cloud-service-dependencies)
- [Data possibly processed by third party services](####data-possibly-processed-by-third-party-services)
- [Android permissions requested by the application](##android-permissions-requested-by-the-application)
- [License](##license)

## Introduction
This privacy policy covers the use of the 'Remède' (https://github.com/camarm-dev/remede) Android application.

It may not be applicable to other software produced or released by Armand Camponovo aka camarm-dev (https://github.com/camarm-dev/remede)

## Compliance with data regulations

Remède is [GDPR](https://commission.europa.eu/law/law-topic/data-protection_en?), [HIPAA](https://www.hhs.gov/hipaa/index.html) and [CCPA](https://oag.ca.gov/privacy/ccpa/regs) privacy regulations compliant.

Remède when running does not use, collect, store or share any statistics, personal information or analytics from its users, is devices or their use of these, other than Android operating system built in mechanisms that are present for all the mobile applications.

Remède does not contain any advertising sdk, nor tracker of the user, his device or their use of these.

Cookies are not used, stored or shared, at any point.

All external interactions require user action (pressing a button at least) unless explicitly configured (by the user) to automatically do so, which is always disabled by default.

## Third party cloud service dependencies

Note that Remède:

* Relies on The "Wiktionnaire" Database and api (https://fr.m.wiktionary.org/wiki/Wiktionnaire:Page_d%E2%80%99accueil) to retrieve information in order to perform the search and display definition of the word(s) searched by the user. Only if the user accepts it explicitly. This service may store user information(s) and data(s) allowing identification. Please refer to the [wiktionary's privacy policy](https://foundation.m.wikimedia.org/wiki/Policy:Privacy_policy) for detailed information on how they handle user data.


* Allows online database(s) downloading, upon user activation and is set for, relying on any external database service. Database(s) downloaded are stored and used locally on the user’s device. Optionally, this service(s) may store user information(s) and data(s) allowing identification. Please refer to the service's privacy policy for detailed information on how they handle user data.

* Allows online caller phone number verification, validation or reporting, upon user configure and activate it, relying on external(s) cloud service(s).
User credentials (API key) of all service(s) are stored locally on the user’s device and are only used for authentication with the official endpoints.
Percase this service(s) may store user information(s) and data(s) allowing identification. Please refer to the service's privacy policy for detailed information on how they handle user data.

#### Data possibly processed by third party services

__No personal data is sent to or otherwise shared with anyone. Data collected by third party services is by the operation of the device running Remède and without support or participation from 'Remède'.__

The only known possible data leaks _(to the third-party servers)_ are the following:
2. User's device IP address
5. date and time stamp, time difference to GMT.
6. Access status/HTTP status code.
7. Browser, operating system, interface, language, version of the browser software, user Agent and all the information possibly available on the http header.
 
Third party services do not necessarily collect all of this data _(always refer to the service's privacy policy)_.

 <!-- Remède specific licenses of libraries used in the application can be accessed from About section. - Not useful actually -->

## Android permissions requested by the application
Note that Remède application requires the following android platform permissions:

* “INTERNET" android permission in order to be able to perform status retrieval, parsing or checking, downloading or updating database, process instant query, Only at the explicit request of the user.

* "MANAGE_EXTERNAL_STORAGE" _(Android 11+)_ or "READ/WRITE_EXTERNAL_STORAGE" _(Android 10)_ android permission in order to be able to perform file access from automated workflow. Only at the explicit request of the user or automatically if configured to do so.

* "POST_NOTIFICATIONS" android permission in order to be able to Show notifications.

* "PACKAGE_USAGE_STATS" android permission in order to be able to perform feature: Recent Apps, only for checking whether an app has been used recently.

## License
[MIT License](https://mit-license.org/)

__Copyright (c) 2024 Armand Camponovo (camarm-dev)__
