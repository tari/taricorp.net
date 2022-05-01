---
title: Managing Google Photos duplicates with Python
slug: google-photos-dedupe-attempt
draft: true
date: 2022-04-30T04:05:40.080Z
categories:
  - Software
tags:
  - google
  - photos
  - api
  - gcloud
  - lightroom
  - python
  - sqlite
  - sqlalchemy
  - giving-up
---
I recently had a bit of a problem with the files that had ended up in Google Photos on my account: the Google Drive desktop synchronization app seemed to have noticed the many (reasonably-high-resolution) thumbnails that my local photo management application (Lightroom) creates, and had uploaded many near-duplicate images.

It seems this wasn't a problem with the old "[Backup and Sync](https://support.google.com/drive/answer/7638428?hl=en)" application because it supported excluding some files from backup (so I could have it ignore the directory that thumbnails get put into), but the new Drive application lacks such a feature.

While Google's sync tool does know how to avoid uploading exact duplicates of photos, it doesn't do any similarity matching on image content, so thumbnails (with the same content but lower resolution) and alternate formats (sidecar JPEGs that go along with camera raw files) end up duplicated in the Google Photos library. I have previously ignored the duplicates in alternate formats because they weren't too annoying, but when the sync tool uploaded a few thousand duplicate thumbnails I felt the need to do something about it.

## Existing programs

There aren't many existing options for managing duplicate items like this. Doing a web search for "Google Photos remove duplicates" mostly gives back content farm-style articles that talk about how Photos provides some duplicate-finding features (yes, but they're limited) and usually go on to suggest some nonfree application for finding duplicates on your local computer. These are all unhelpful because:

 * I don't have duplicates on my local computer, and want to clean up the duplicates in the Google library so it's easier to browse (and to save some space)
 * The official duplicate finding tool doesn't appear to look at visual similarity, so misses the thumbnails I want to remove
 * They're trying to sell me something that doesn't do what I want

I did discover [Rémi Mikel's duplicate finding tool](https://duplicates-google-photos.remikel.fr/) which seemed like a step in the right direction, but seemed to perform too badly to be very useful (probably because there are thousands of images that I want to get rid of, and it tries to display all of them in your browser). It did suggest an approach I could take to do this myself though, by using the public [Google Photos API](https://developers.google.com/photos/library/guides/overview).

## Rolling an API client

With some ideas in mind, I wrote a little Python application to gather data. Using the public API is fairly straightforward; the most difficult part is probably in simply setting something up to be able to authenticate with my own credentials and access my photos.

### Configuring authentication

In the Google Cloud console, I created a project and enabled the [Photos Library API](https://console.cloud.google.com/apis/api/photoslibrary.googleapis.com/) for it, then created an OAuth client ID that I could use in my application. Since the steps are easier to illustrate than describe, here are screenshots of the process after having created a project.

* Enable the Photos Library API in the API library
  
  ![The Photos Library API shown in the API library, with a blue "Enable" button](/2022/google-photos-dedupe-attempt/01-enable-api.png)
* Create an OAuth consent screen for the application. This gets shown to users when providing the application access to the data in their Google account. It's fine to make this an "External" application.
  * This requires you to fill in an app name and some email addresses, but what exactly those are is up to you; they don't really matter if this project is only going to be for personal use, as it was in my case.
    ![Select "Internal" or "External" users to begin creating an OAuth consent screen.](/2022/google-photos-dedupe-attempt/02-oauth-consent.png)
   *  When asked to select scopes for the app, select the relevant ones for the Photos Library API. `photoslibrary` and `photoslibrary.sharing` are sufficient for this use case. Any scopes that aren't enabled here won't be available to the application (permission will be denied) when run.
     ![](/2022/google-photos-dedupe-attempt/03-oauth-scopes.png)
   * The third step adds users to the allowlist for a testing app, which is the default configuration. Non-testing apps are available to the public but may require review by Google before they can be published, but since this is for personal use on my own computer it's fine to let it stay as a test app. I added my own email address to the list of test users and continued on.

* Having configured the consent screen, we can now create a new OAuth client ID, in the API credentials page

  * Choose to create new credentials, and select "OAuth client ID".
    ![Selecting "Create credentials" drops down a menu, where one option is to create an OAuth client ID](/2022/google-photos-dedupe-attempt/04-create-credentials.png)

  * Set the Application type to Desktop and fill in a name. This program runs locally and is not a web application, so the type must be Desktop in order for the local authentication flow to be permitted.

    ![Creating a client ID requires the application type be specified and a name provided](/2022/google-photos-dedupe-attempt/05-client-id.png)

   * Download the JSON for the created client details after the client is created. The program will need to provide this to Google when logging in.

     ![After creating a client ID, the ID and a client secret are shown, with a button available to download JSON](/2022/google-photos-dedupe-attempt/06-client-created.png)

I saved the downloaded file as `client_secret.json` and then got to actually writing my program.

### Downloading data

Rather than walk through the process of writing the program I did, I'll simply present the code after describing what I chose to have it do.

Since I was taking inspiration from Mikel's tool, I knew I only wanted to gather photo metadata to compare, which is largely returned when simply listing a user's library.  To play with that data interactively and figure out what I wanted to filter on to delete, I decided to store it in a SQLite database, since that would be easy to query later. With that in mind, I simply made the program call [`mediaItems.list`](https://developers.google.com/photos/library/reference/rest/v1/mediaItems/list) in a loop, taking a page (100 items) at a time until there were no more pages. For each item, it extracts the metadata I care about and stores it in the database.

To work with the database I opted to use [SQLAlchemy](https://www.sqlalchemy.org/) simply because it was a convenient way to manage types that the database might not directly understand and run queries in a slightly less cumbersome way. In total, these libraries are needed to run the below code (all installable from [PyPI](https://pypi.org/)):
 * `google-api-python-client`
 * `google-auth-oauthlib`
 * `SQLAlchemy`
 * `python-dateutil`

With that out of the way, here's the actual code I wrote:

```python
import datetime as dt

import dateutil.parser
import googleapiclient.discovery
from google_auth_oauthlib.flow import InstalledAppFlow
from sqlalchemy import Column, String, create_engine, DateTime, Integer, Float, Interval
from sqlalchemy.orm import declarative_base, Session

Base = declarative_base()


class Photo(Base):
    __tablename__ = 'photos'

    id = Column(String(256), primary_key=True)
    filename = Column(String(128), nullable=False)
    mime_type = Column(String(64), nullable=False)
    creation_time = Column(DateTime(timezone=True), index=True)
    width = Column(Integer())
    height = Column(Integer())
    camera_make = Column(String(64))
    camera_model = Column(String(64))
    focal_length = Column(Float())
    f_stop = Column(Float())
    iso_equivalent = Column(Integer())
    exposure_time = Column(Interval())


engine = create_engine("sqlite:///photos.sqlite", future=True)
Base.metadata.create_all(engine)

# No idea how to restore saved credentials, so don't try. Many examples use
# oauth2client.file.Storage but that doesn't work, at least in recent versions:
# https://github.com/googleapis/google-api-python-client/issues/491
credentials = None
if credentials is None or credentials.invalid:
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secret.json',
        scopes=['https://www.googleapis.com/auth/photoslibrary'],
    )
    credentials = flow.run_local_server(
        host='localhost',
        port=8000,
        open_browser=True,
    )
print('Authenticated OK')

service = googleapiclient.discovery.build('photoslibrary', 'v1', credentials=credentials, static_discovery=False)

with Session(engine) as session:
    page_token = None
    while True:
        session.begin()
        response = service.mediaItems().list(pageSize=100, pageToken=page_token).execute()
        for item in response.get('mediaItems', []):

            photo = Photo(
                id=item['id'],
                filename=item['filename'],
                mime_type=item['mimeType'],
            )
            metadata = item.get('mediaMetadata')
            if metadata is not None:
                if 'creationTime' in metadata:
                    photo.creation_time = dateutil.parser.isoparse(metadata['creationTime'])
                if 'width' in metadata:
                    photo.width = int(metadata['width'])
                if 'height' in metadata:
                    photo.height = int(metadata['height'])
                if 'photo' in metadata:
                    photo_meta = metadata['photo']
                    photo.camera_make = photo_meta.get('cameraMake')
                    photo.camera_model = photo_meta.get('cameraModel')
                    photo.focal_length = photo_meta.get('focalLength')
                    photo.f_stop = photo_meta.get('apertureFNumber')
                    photo.iso_equivalent = photo_meta.get('isoEquivalent')
                    if 'exposureTime' in photo_meta and photo_meta['exposureTime'].endswith('s'):
                        photo.exposure_time = dt.timedelta(seconds=float(photo_meta['exposureTime'][:-1]))

            print(photo.id)
            session.merge(photo)

        session.commit()
        page_token = response.get('nextPageToken')
        if page_token is None:
            break
```

Running this opens a web browser to grant access to a Google account, and when authentication succeeds it then grabs metadata for every item in the Google Photos library, printing the ID of each item while it goes.

## Finding unwanted thumbnails

To find the thumbnails I don't want, I can start by manually running queries against the generated SQLite database. It turns out the unwanted thumbnail files have a common filename format that appears to be a UUID, and they're always `.dng` files. It wasn't too difficult to search for the files that have matching filenames and (to avoid deleting those that don't seem to correspond to any other image) avoid matching those that don't appear to have an original file (taken by the same camera at the same time) already known:

```sql
SELECT *
FROM photos AS main
WHERE filename LIKE '________-____-____-____-____________.dng'
AND EXISTS(
    SELECT id from photos
    WHERE creation_time = main.creation_time
      AND camera_make = main.camera_make
      AND camera_model = main.camera_model
      AND id != main.id
)
```

This returns 3651 rows from my library, so then the problem is how to take those images (probably by ID) and remove them from Google Photos.

## Removing unwanted images

Unfortunately, the Google Photos API [doesn't provide any way to delete photos](https://issuetracker.google.com/issues/109759781#comment72). This seems to be largely because a malicious application could use it to delete all of a user's photos (a reasonable concern!), but it makes what I want to do difficult. One user on the above bug suggests using the API to add photos to a new album, from which the user can delete photos with relative ease, which I think is a reasonable choice.

I wrote another script (copying the authentication code from before into a new `auth` module for reuse), taking the ID of an album on the command line, as well as the name of a file containing item IDs:

```python
import sys
import googleapiclient.discovery

album_id = sys.argv[1]
item_ids_file = sys.argv[2]

from .auth import credentials

service = googleapiclient.discovery.build('photoslibrary', 'v1', credentials=credentials, static_discovery=False)

with open(item_ids_file, 'r') as f:
    item_ids = f.readlines()


def chunks():
    # batchAddMediaItems takes no more than 50 items per call
    for i in range(0, len(item_ids), 50):
        yield item_ids[i:i+50]

for chunk in chunks():
    service.albums().batchAddMediaItems(albumId=album_id, body=dict(
        mediaItemIds=chunk
    )).execute()
```

I created an album manually via the API, and created a file with one ID per line by exporting the results of the above SQL query to a CSV file with only one column (the ID of the item). Unfortunately, this fails with an HTTP 400, complaining that `Request contains an invalid media item id.` After some experimentation (manually using the API to get a single ID and add it to an album), I realized the problem was an unfortunate but intentional API limitation:

> Note that you can only add media items that have been uploaded by your application to albums that your application has created.

..so it turns out it's impossible to do anything useful via the API alone. It might be possible to do this via browser automation like [a "delete all photos" tool](https://github.com/mrishab/google-photos-delete-tool/) I happened across, but that's a bigger hack than I'm interested in right now, so I'm forced to give up on the goal for now.

## Other uses of the data

I had a few other ideas of interesting things to do with the database I collected in addition to the desired "remove unwanted thumbnails":

 * Locate other duplicates by finding images with similar metadata (camera, capture time, ISO equivalent, shutter speed, ...). This would probably match raw files that have matching sidecar JPEGs, where I would likely prefer to remove the raws since the JPEGs tend to be better suited to browsing and I don't use Google Photos as a repository for high-quality originals.
 * Find files that exist in Google Photos but not on my local storage. It's possible that some files would have been accidentally deleted that I could recover a version of (not the originals, probably) from the web. It's also possible there would be a lot of false positives of photos that I intentionally deleted and would want to remove from Google, though.

In general, there are some interesting possibilities for ways in which photos data in this form could be swizzled into a helpful outcome, but it's unfortunate that the APIs provided for Google Photos mean there aren't many ways the data can be used to any meaningful end.