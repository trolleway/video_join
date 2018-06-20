
import argparse, os
import subprocess
from gooey import Gooey, GooeyParser
import tempfile


import subprocess
import re
from decimal import Decimal
 
 
running = True


def get_video_length(filepath):
    cmd = 'ffmpeg -i "{filepath}" '.format(filepath=filepath)
    out = subprocess.Popen(cmd, shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    stdout,stderr = out.communicate()
    lines = stdout
    metadata = {}
    for l in lines.splitlines():
        l = l.strip()
        if l.startswith('Duration'):
            metadata['duration'] = re.search('Duration: (.*?),', l).group(0).split(':',1)[1].strip(' ,')
            t = metadata['duration'].split(':')
            seconds = float( (t[0]*60*60)+(t[1]*60)+t[2] )
            
            metadata['bitrate'] = re.search("bitrate: (\d+ kb/s)", l).group(0).split(':')[1].strip()
        if l.startswith('Stream #0:0'):
            metadata['video'] = {}
            metadata['video']['codec'], metadata['video']['profile'] = \
                [e.strip(' ,()') for e in re.search('Video: (.*? \(.*?\)),? ', l).group(0).split(':')[1].split('(')]
            metadata['video']['resolution'] = re.search('([1-9]\d+x\d+)', l).group(1)
            metadata['video']['bitrate'] = re.search('(\d+ kb/s)', l).group(1)
            metadata['video']['fps'] = re.search('(\d+ fps)', l).group(1)
        if l.startswith('Stream #0:1'):
            metadata['audio'] = {}
            metadata['audio']['codec'] = re.search('Audio: (.*?) ', l).group(1)
            metadata['audio']['frequency'] = re.search(', (.*? Hz),', l).group(1)
            metadata['audio']['bitrate'] = re.search(', (\d+ kb/s)', l).group(1)
    return seconds
    
@Gooey(optional_cols=2, program_name="concatenate videos")
def main():
    settings_msg = "Concatenate videos in FFMPEG whthout re-encoding \n" \
                 'New file will be saved to source folder'
    parser = GooeyParser(description=settings_msg)
    parser.add_argument('--verbose', help='be verbose', dest='verbose',
                      action='store_true', default=False)
    subs = parser.add_subparsers(help='commands', dest='command')

    concatenate_parser = subs.add_parser('concatenate', help='Concatenate videos')
    concatenate_parser.add_argument('videos',
                           help='Video files',
                           type=str, widget='MultiFileChooser')  
    concatenate_parser.add_argument('--clip',
                           help='Clip 1 second from begin and end of each source video. Requires same space in system temp folder.',
                           action='store_true',  dest = 'clip')
    concatenate_parser.add_argument('--filename',
                           help='New file name, withouth exstension',
                           type=str, default = 'joined')
    concatenate_parser.add_argument('--seconds',
                           help='Trim seconds from each input file',
                           type=str, default = '1',gooey_options={
            'validator': {
                'test': '0 <= int(user_input) <= 14',
                'message': 'Must be between 0 and 14'
            }})
                           


    args = parser.parse_args()
    if args.command == 'concatenate':
        VIDEOS = args.videos
        FILENAME = args.filename
        videos_list = VIDEOS.split(";")
        folder = os.path.dirname(videos_list[0])
        video_extension = os.path.splitext(videos_list[0])[1]
        seconds = args.seconds
    
        print args
        if args.clip:
            temp_videos = list()
            for video in videos_list:
                extension = os.path.splitext(video)[1]
                tf = tempfile.NamedTemporaryFile(suffix=extension,delete=False)
                
                '''
                cmd = 'ffprobe -i "{video}" -show_entries format=duration -v quiet -of csv="p=0"'.format(video=video)
                #duration = subprocess.check_output(['ffprobe', '-i', video,'-show_entries format=duration -v quiet -of csv="p=0"'])
                #out = subprocess.Popen(['ffprobe', '-i', video,' -show_entries format=duration -v quiet -of csv="p=0"'], 
                out = subprocess.Popen(cmd, shell=True,
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT)
                stdout,stderr = out.communicate()
                duration = float(stdout)
                #print duration
                '''
                duration = get_video_length(video)
               
                if float(duration) > 5:
                    cmd = 'ffmpeg -ss {seconds} -i "{video}" -t {duration} -qscale:v 2 {output}'.format(video=video, seconds = seconds, output=tf.name+extension, duration=str(duration-float(seconds)*2))
                elif 3 <= float(duration) <= 5:
                    cmd = 'ffmpeg -ss {seconds} -i "{video}" -t {duration} -qscale:v 2 {output}'.format(video=video, seconds = seconds, output=tf.name+extension, duration=str(duration-float(seconds)*2))
                else:
                    #3-second clips copying withoth clip
                    cmd = 'ffmpeg -y -safe 0 -f concat -i {tf} -c copy  -vcodec copy  "{filename}"'.format(tf=video,filename=tf.name+extension)
                os.system(cmd)
                temp_videos.append(tf.name+extension)
                print cmd
            videos_list = temp_videos
            print temp_videos
        else:
            pass
        
        ffmpeg_concatenate_list = r''
        for file in videos_list:
          cmd = "file '"+file+"'\n"
          ffmpeg_concatenate_list += cmd
        
        tf = tempfile.NamedTemporaryFile(delete=False)
        print tf.name
        text_file = open(tf.name, "w")
        text_file.write(ffmpeg_concatenate_list)
        text_file.close()
        
        cmd = 'ffmpeg -y -safe 0 -f concat -i {tf} -c copy  -vcodec copy  "{filename}"'.format(tf=tf.name,filename=os.path.join(folder,FILENAME)+''+video_extension)
        print cmd
        os.system(cmd)
        
        #os.unlink(tf.name)

if __name__ == '__main__':
  main()
