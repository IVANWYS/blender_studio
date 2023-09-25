from django.shortcuts import render, redirect
from static_assets.models import Video, VideoTrack, StaticAsset, M3u8Playlist, M3u8Source
from django.contrib import messages
import re
# Create your views here.


def files_upload(request):
    
    context = {
        "data": M3u8Playlist.objects.all,
        "playlist": M3u8Playlist.objects.filter(types="playlist"),
    }
    return render(request, 'm3u8_upload/files_upload.html', context)

def send_files(request):
    if request.method == "POST":
        user_id = request.user.id
        upload_Video = request.FILES.get('upload_Video', "")
        uploadThumbnail = request.FILES.get('uploadThumbnail', "")
        v_Duration = request.POST.get("duration", "")
        # Subtitles
        uploadTrack_EN = request.FILES.get('uploadTrack_EN', "")
        uploadTrack_CN = request.FILES.get('uploadTrack_CN', "")
        uploadTrack_HK = request.FILES.get('uploadTrack_HK', "")
        # M3U8 files
        title = request.POST.get("filename", "")
        upload_M3U8_Video = request.FILES.getlist("upload_M3U8_Video")
        upload_M3U8_Audio = request.FILES.getlist("upload_M3U8_Audio")
        upload_M3U8_Playlist = request.FILES.get("upload_M3U8_Playlist", "")

        v_id = set_video(upload_Video, uploadThumbnail, user_id)
        vt_id = set_duration(v_Duration, v_id)

        # Video Track
        set_video_track(uploadTrack_EN, uploadTrack_CN, uploadTrack_HK, vt_id)
        
        # M3U8
        set_m3u8(title, upload_M3U8_Playlist, upload_M3U8_Video, upload_M3U8_Audio, v_id)

    messages.success(request, 'Upload Successful !')

    return redirect("files_upload")



def set_video(upload_Video, uploadThumbnail, user_id):
    v_source = StaticAsset(source=upload_Video, source_type="video", content_type="video/mp4", thumbnail=uploadThumbnail, user_id=user_id, license_id="1")
    v_source.save()
    v_id = v_source.id
    
    return(v_id)


def set_duration(v_Duration, v_id):
    if v_Duration != "":
        Duration_List = re.split('\W+', v_Duration.strip())
        hour = Duration_List[0].zfill(2)
        minute = Duration_List[1].zfill(2)
        second = Duration_List[2].zfill(2)
        Duration = f"{hour}:{minute}:{second}"
    else:
        Duration = "00:01:00"
        
    Video.objects.update_or_create(
            static_asset_id=v_id, defaults={'duration': Duration},)
    
    vt_id = Video.objects.values_list(
            'id').filter(static_asset_id=v_id)[0]
    vt_id = vt_id[0]

    return(vt_id)


def set_video_track(uploadTrack_EN, uploadTrack_CN, uploadTrack_HK, vt_id):
    if uploadTrack_EN != "":
        VideoTrack(video_id=vt_id, source=uploadTrack_EN, language="en-US").save()
    if uploadTrack_CN != "":
        VideoTrack(video_id=vt_id, source=uploadTrack_CN, language="zh-hans").save()
    if uploadTrack_HK != "":
        VideoTrack(video_id=vt_id, source=uploadTrack_HK, language="zh-hant").save()


def set_m3u8(title, upload_M3U8_Playlist, upload_M3U8_Video, upload_M3U8_Audio, v_id):
    if title != "":

        m3u8_playlist = M3u8Playlist(title=title, types="playlist", source=upload_M3U8_Playlist, sVideo_id = v_id)
        m3u8_playlist.save()
        playlist_id = m3u8_playlist.id

        for file in upload_M3U8_Video:
            if file.name != '.DS_Store':
                M3u8Source(title_id = playlist_id, types="video", source=file).save()
        for file in upload_M3U8_Audio:
            if file.name != '.DS_Store':
                M3u8Source(title_id = playlist_id, types="audio", source=file).save()

    print("- Upload Successful -")