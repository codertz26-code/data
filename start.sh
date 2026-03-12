#!/data/data/com.termux/files/usr/bin/bash

echo "🚀 Inaanzisha Data Collector System..."

# Hakikisha tumefika kwenye folder sahihi
cd /sdcard/Download

# Unda folder za mradi kama hazipo
mkdir -p data-collector/{collector,server,dashboard,database}

# Nakili files kwenye folders sahihi
cp collector.py data-collector/collector/
cp logger.py data-collector/collector/
cp config.py data-collector/collector/
cp server.py data-collector/server/
cp index.html data-collector/dashboard/
cp style.css data-collector/dashboard/
cp script.js data-collector/dashboard/

# Anzisha collector kwenye background
echo "📡 Inaanzisha collector..."
cd data-collector/collector
python collector.py &

# Subiri sekunde chache
sleep 3

# Anzisha server
echo "🌐 Inaanzisha server..."
cd ../server
python server.py

# Script itaendelea kukimbia hapa hadi uikome kwa Ctrl+C
