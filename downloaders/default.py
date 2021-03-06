
import mimetypes, time

VIDEO_DOMAINS = [
		'youtube.com',
		'youtu.be',
		'v.redd.it',
		'gfycat.com',
		'm.youtube.com'
	]

IMAGE_DOMAINS = [
	'i.redd.it',
	'i.imgur.com',
	'cdna.artstation.com'
]

def domains():
	return VIDEO_DOMAINS + IMAGE_DOMAINS

def create_jobs(item, library_folder, config, rs):
	domain = item['data']['domain']
	name = item["data"]["name"]
	
	do_commands = []
	
	# this object gets attached after
	metadata = {'downloader_version': 'default/1.0', 'jobs_generated': int(time.time())}
	
	if domain not in domains():
		raise NotImplementedError('Downloader default.py received an item with an unsupported domain.')
		
		
	# check for a thumbnail from reddit
	thumbnail = item['data']['thumbnail']
	if thumbnail and type(thumbnail) == str:
		ext = thumbnail.split('?')[0].split('.')[-1]
		fname = f'{name}.thumb_small.{ext}'
		metadata['thumb'] = fname
		
		command = [
			'python3', 'rqget.py',
			'-O', f'{library_folder}/{domain}/thumbs/{fname}',
			thumbnail
		]
		
		if config.get('proxy'):
			command += ['--proxy', config.get('proxy')]
		
		do_commands.append(command)
	
	if domain in VIDEO_DOMAINS or item['data']['url'].endswith('gifv'):
		metadata['class'] = 'video'
		
		if 'youtu' in domain and rs.get('youtube', {}).get('download_videos', False) == False:
			return []
		
		if 'v.redd.it' in domain and rs.get('reddit', {}).get('download_reddit_video', True) == False:
			return []
		
		command = [
			'youtube-dl',
			'--write-thumbnail',
			'--write-description',
			'--limit-rate', '2M', # 2 MB/s
			'-o', f'{library_folder}/{domain}/{name}.%(title)s-%(id)s.%(ext)s',
			item['data']['url']
		]
		
		if domain == 'gfycat.com':
			command.pop(command.index('--write-description'))
		
		if 'proxy' in config:
			command.extend( ['--proxy', config['proxy']] )
		
		if 'youtu' in domain:
			command.extend( ['--format', '720p[filesize<512MB]/720p60[filesize<512MB]/1080p[filesize<128MB]/1080p60[filesize<64MB]/best[filesize<512MB]/worst'] )
			
		do_commands.append(command)
	
	elif domain in IMAGE_DOMAINS:
		metadata['class'] = 'image'
		
		if domain == 'cdna.artstation.com':
			if 'image/' not in mimetypes.guess_type(item['data']['url'].split('?')[0])[0]:
				return
		
		command = [
			'python3', 'rqget.py',
			'-O', f'{library_folder}/{domain}/{name}.{item["data"]["url"].split("?")[0].split("/")[-1]}',
			item['data']['url']
		]
		
		if config.get('proxy'):
			command += ['--proxy', config.get('proxy')]
		
		do_commands.append(command)
		
		if domain == 'i.redd.it':
			do_commands.append( ['echo', 'lmao'] )
	
	if len(do_commands) > 0:
		return [metadata] + do_commands
	else:
		return []
