# Video Streaming: HLS, AVPlayer, and MP4 Optimization

Knowledge for serving video from S3/self-hosted infrastructure to web and iOS clients.

## The MOOV Atom Problem (MP4 Streaming)

MP4 files contain a metadata section called the **MOOV atom**. Most encoders write it at the **end** of the file by default. A player trying to stream the file must then download the entire file before it can begin playback.

For streaming, the MOOV atom must be at the **front** of the file.

### Fix with ffmpeg (copy streams, no re-encode)

```bash
ffmpeg -i input.mp4 -movflags faststart -acodec copy -vcodec copy output.mp4
```

### Batch fix an entire library

```bash
find /mnt/nas/media -name "*.mp4" | while read f; do
  ffmpeg -i "$f" -movflags faststart -acodec copy -vcodec copy "${f%.mp4}_fixed.mp4" && \
  mv "${f%.mp4}_fixed.mp4" "$f"
done
```

### Verify MOOV atom placement

```bash
ffprobe -v quiet -print_format json -show_format input.mp4 | grep -i moov
# Or check with MP4Box:
mp4info input.mp4 | grep -i moov
```

After fixing: browsers can start playback immediately and seek without downloading the full file using HTTP 206 Partial Content range requests.

## AVPlayer (iOS) Critical Limitation

**AVPlayer does NOT support HTTP range requests.** It downloads the entire file before playing, regardless of:
- Whether the server supports `Accept-Ranges: bytes`
- Whether the MOOV atom is at the front
- Whether you use S3, CloudFront, or any other CDN

This is an Apple design decision. The only fix is to use **HLS**.

## HLS (HTTP Live Streaming)

HLS is Apple's own protocol and is fully supported by AVPlayer. It streams video as small segments and starts playback almost immediately.

### Generate HLS with ffmpeg

```bash
ffmpeg -i input.mp4 \
  -codec: copy \
  -start_number 0 \
  -hls_time 10 \
  -hls_list_size 0 \
  -f hls \
  output.m3u8
```

Output: `output.m3u8` manifest + `output0.ts`, `output1.ts`, ... (10-second segments)

### HLS with multiple bitrates (adaptive)

```bash
# 1080p
ffmpeg -i input.mp4 -vf scale=-2:1080 -c:v h264 -b:v 5000k -c:a aac -b:a 192k \
  -hls_time 10 -hls_list_size 0 -f hls 1080p.m3u8

# 720p
ffmpeg -i input.mp4 -vf scale=-2:720 -c:v h264 -b:v 2800k -c:a aac -b:a 128k \
  -hls_time 10 -hls_list_size 0 -f hls 720p.m3u8

# Master playlist (create manually)
cat > master.m3u8 <<'EOF'
#EXTM3U
#EXT-X-STREAM-INF:BANDWIDTH=5000000,RESOLUTION=1920x1080
1080p.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=2800000,RESOLUTION=1280x720
720p.m3u8
EOF
```

### AVPlayer pointing to HLS

```swift
let url = URL(string: "https://your.domain.com/videos/output.m3u8")!
let asset = AVURLAsset(url: url)
let item = AVPlayerItem(asset: asset)
let player = AVPlayer(playerItem: item)
```

## S3 Setup for HLS

```bash
# Upload all HLS files (manifest + segments)
aws s3 sync ./hls-output/ s3://your-bucket/videos/video1/ \
  --content-type "application/x-mpegURL" \
  --exclude "*" --include "*.m3u8"

aws s3 sync ./hls-output/ s3://your-bucket/videos/video1/ \
  --content-type "video/MP2T" \
  --exclude "*" --include "*.ts"
```

Point AVPlayer at: `https://your-bucket.s3.region.amazonaws.com/videos/video1/output.m3u8`

## AWS MediaConvert (Production HLS)

For automated MP4 → HLS conversion at scale:

1. Go to AWS Elemental MediaConvert in the console
2. Create a job with your S3 MP4 as input
3. Add HLS output group → set segment duration (6-10s)
4. Set S3 output path
5. Submit → outputs `.m3u8` + `.ts` files to S3 automatically

## CloudFront (Optional)

CloudFront sits in front of S3 for caching and reduced egress costs. Not required for HLS to work, but beneficial at scale.

RTMP distributions (old) are discontinued — CloudFront now serves HLS over HTTPS.

## Jellyfin Integration

Jellyfin handles both cases automatically:
- **Direct play**: MP4 with faststart MOOV atom streams immediately in browsers
- **Transcoding to HLS**: Jellyfin does this on-the-fly for clients that need it (including iOS via the Jellyfin app)
- **iOS Jellyfin app**: Uses Jellyfin's built-in HLS transcoding — no manual pre-conversion needed

For the self-hosted media suite, pre-processing MP4s with `faststart` is the only extra step needed. Jellyfin covers the rest.

## Post-Processing Hook (Sonarr/Radarr)

Add to Sonarr/Radarr under **Settings → Connect → Custom Script**:

```bash
#!/usr/bin/env bash
# /home/user/arr-suite/scripts/faststart.sh
FILE="$radarr_moviefile_path"  # or sonarr_episodefile_path
[[ "$FILE" == *.mp4 ]] || exit 0
TMP="${FILE%.mp4}_tmp.mp4"
ffmpeg -i "$FILE" -movflags faststart -acodec copy -vcodec copy "$TMP" && mv "$TMP" "$FILE"
```

## Decision Matrix

| Client | Protocol | What to do |
|---|---|---|
| Browser | HTTP range requests (206) | MP4 with `faststart` |
| iOS AVPlayer (direct) | HLS only | ffmpeg → .m3u8 or AWS MediaConvert |
| iOS Jellyfin app | HLS (Jellyfin transcodes) | Nothing extra needed |
| Android/desktop players | Range requests or HLS | MP4 with `faststart` covers both |
| Jellyfin web | Range + HLS fallback | MP4 with `faststart` |

## Quick Reference

```bash
# One-shot fix MOOV atom
ffmpeg -i in.mp4 -movflags faststart -c copy out.mp4

# One-shot generate HLS
ffmpeg -i in.mp4 -codec: copy -hls_time 10 -hls_list_size 0 -f hls out.m3u8

# Check if S3 object supports range requests
curl -I https://bucket.s3.region.amazonaws.com/video.mp4 | grep Accept-Ranges
# Should show: Accept-Ranges: bytes
```

## Sources

- Stack Overflow: AVPlayer + S3 streaming (Ermiya Eskandary, Jan 2022)
- Apple HLS documentation
- ffmpeg docs: `-movflags faststart`, `-f hls`
