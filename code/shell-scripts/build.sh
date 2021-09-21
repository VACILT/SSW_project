cd testbook
cat stations.txt | parallel 'papermill analysis_per_station.ipynb analysis_{}.ipynb -p station {} &> /home/hochatmstud/bene/logs/{}.log'
cd ../
jupyter-book clean testbook/
jupyter-book build -W -n --keep-going testbook/
