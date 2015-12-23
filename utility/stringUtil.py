import re
def match_docheader(line):
		return re.search(ur"<DOCNO>(.*?)</DOCNO>", line)

def split_words(line):
	regex = ur"[\d*|<.*?>|'|,|.|:|?|!|\"|\(|\)|/|;|\-|\[|\]]"
	l = re.sub(regex, ' ', line).strip()

	regex = ur"\s+"
	line_words = re.split(regex, l)
	return line_words

def stop_word():
	stopword = ['a','about','above','across','after','again','against','all','almost','alone',
	'along','already','also','although','always','among','an','and','another','any','anybody',
	'anyone','anything','anywhere','are','area','areas','around','as','ask','asked','asking',
	'asks','at','away','b','back','backed','backing','backs','be','became','because','become',
	'becomes','been','before','began','behind','being','beings','best','better','between','big',
	'both','but','by','c','came','can','cannot','case','cases','certain','certainly','clear',
	'clearly','come','could','d','did','differ','do','does','done',
	'down','down','downed','downing','downs','during','e','each','early','either','end','ended',
	'ending','ends','enough','even','evenly','ever','every','everybody','everyone','everything',
	'everywhere','f','face','faces','fact','facts','far','felt','few','find','finds','first','for',
	'four','from','full','fully','g','gave','general',
	'generally','get','gets','give','given','gives','go','going','good','goods','got','great',
	'greater','greatest','group','grouped','grouping','groups','h','had','has','have','having','he',
	'her','here','herself','high','higher','highest','him','himself','his','how','however','i','if',
	'important','in','into','is','it','its',
	'itself','j','just','k','keep','keeps','kind','knew','know','known','knows','l','large','largely',
	'last','later','latest','least','less','let','lets','like','likely','long','longer','longest',
	'm','made','make','making','man','many','may','me','men','might','more','most',
	'mostly','mr','mrs','much','must','my','myself','n','necessary','need','needed','needing','needs',
	'never','new','new','newer','newest','next','no','nobody','non','noone','not','nothing','now',
	'nowhere','number','numbers','o','of','off','often','old','older','oldest','on','once','one','only',
	'open','opened','opening','opens','or','order','ordered','ordering','orders','other','others',
	'our','out','over','p','part','parted','parting','parts','per','perhaps','place','places','point',
	'pointed','pointing','points','possible','problem',
	'problems','put','puts','q','quite','r','rather','really','right','right','room','rooms','s','said',
	'same','saw','say','says','second','see','seem','seemed','seeming','seems','sees','several',
	'shall','she','should','show','showed','showing','shows','side','sides','since','small','smaller',
	'smallest','so','some','somebody','someone','something','somewhere','state','states','still','still',
	'such','sure','t','take','taken','than','that','the','their','them','then','there','therefore','these',
	'they','thing','things','think','thinks','this','those','though','thought','thoughts','three','through',
	'thus','to','today','together','too','took','toward','turn','turning','turns','two','u','under',
	'until','up','upon','us','use','used','uses','v','very','w','want','wanted','wanting','wants','was','way',
	'ways','we','well','wells','went','were','what','when','where','whether','which','while','who','whole',
	'whose','why','will','with','within','without','work','worked','working','works','would','x','y','year',
	'years','yet','you','young','younger','youngest','your','yours','z',
	]
	return stopword

