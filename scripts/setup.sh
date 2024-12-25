# setup on localhost
export HOST=127.0.0.1
export PORT=$(comm -23 <(seq 1024 65535 | sort) <(ss -tan | awk '{print $4}' | cut -d':' -f2 | grep "[0-9]\{1,5\}" | sort -u) | shuf |
head -n 1)

# invoke thread to get risk free rate (treasury rate)
sleep 1 && python3 ../src/client.py ^IRX --query stock &

# invoke threads to get stock data
sleep 1 && python3 ../src/client.py META --query stock &
sleep 1 && python3 ../src/client.py META --query option &
sleep 1 && python3 ../src/client.py AMZN --query stock &
sleep 1 && python3 ../src/client.py AMZN --query option &
sleep 1 && python3 ../src/client.py AAPL --query stock &
sleep 1 && python3 ../src/client.py AAPL --query option &
sleep 1 && python3 ../src/client.py MSFT --query stock &
sleep 1 && python3 ../src/client.py MSFT --query option &
sleep 1 && python3 ../src/client.py NVDA --query stock &
sleep 1 && python3 ../src/client.py NVDA --query option &
sleep 1 && python3 ../src/client.py NFLX --query stock &
sleep 1 && python3 ../src/client.py NFLX --query option &

# Read tickers from the file
# tickers=$(cat tickers.txt)

# Iterate over each ticker
# for ticker in $tickers; do
#     sleep 1 && python3 ../src/client.py "$ticker" --query stock &
#     sleep 1 && python3 ../src/client.py "$ticker" --query option &
# done

python3.13t ../src/server.py