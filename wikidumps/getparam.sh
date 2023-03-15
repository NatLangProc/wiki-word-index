wget -c https://dumps.wikimedia.org/$1wiki/latest/$1wiki-latest-pages-articles-multistream.xml.bz2
wget -c https://dumps.wikimedia.org/$1wiki/latest/$1wiki-latest-pages-articles-multistream-index.txt.bz2
bzip2 -dk $1wiki-latest-pages-articles-multistream-index.txt.bz2

