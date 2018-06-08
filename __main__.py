
import argparse, os
from gooey import Gooey, GooeyParser
import tempfile

running = True


@Gooey(optional_cols=2, program_name="concatenate videos")
def main():
  settings_msg = 'concatenate videos in FFMPEG whtiouth re-encoding' \
                 'New file will be saved to source folder'
  parser = GooeyParser(description=settings_msg)
  parser.add_argument('--verbose', help='be verbose', dest='verbose',
                      action='store_true', default=False)
  subs = parser.add_subparsers(help='commands', dest='command')

  concatenate_parser = subs.add_parser('concatenate', help='Concatenate videos')
  concatenate_parser.add_argument('videos',
                           help='Video files',
                           type=str, widget='MultiFileChooser')
  concatenate_parser.add_argument('filename',
                           help='New file name, withouth exstension',
                           type=str, default = 'joined')

                           


  args = parser.parse_args()
  if args.command == 'concatenate':
    VIDEOS = args.videos
    FILENAME = args.filename
    videos_list = VIDEOS.split(";")
    folder = os.path.dirname(videos_list[0])
    video_extension = os.path.splitext(videos_list[0])[1]
    ffmpeg_concatenate_list = r''
    for file in videos_list:
      cmd = "file '"+file+"'\n"
      ffmpeg_concatenate_list += cmd
    
    tf = tempfile.NamedTemporaryFile(delete=False)
    print tf.name
    text_file = open(tf.name, "w")
    text_file.write(ffmpeg_concatenate_list)
    text_file.close()
    
    cmd = 'ffmpeg -y -safe 0 -f concat -i {tf} -c copy  -vcodec copy  {filename}'.format(tf=tf.name,filename=os.path.join(folder,FILENAME)+''+video_extension)
    print cmd
    os.system(cmd)
    
    #os.unlink(tf.name)




if __name__ == '__main__':
  main()
