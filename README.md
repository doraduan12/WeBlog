### Usage

1. download and install gStore http://www.gstore.cn/pcsite/help-document.html
2. preprocess data, convert weibodatabase.sql to data.nt: `python processdata.py`
3. begin gstore service: `cd gStore && bin/gbuild weibo ../data.nt && bin/ghttp weibo 12355`

### files

```
.
├── data.nt -- converted data
├── gStore/
├── main.py -- back end functions
├── processdata.log -- generated from processdata.py, which contains all convert-failed lines
├── processdata.py -- convert weibodatabase.sql to data.nt
├── README.md
├── requirements.txt
├── utils_gstore.py -- functions for basic manipulations in gStore
├── utils_weibo.py -- functions for back end
└── weibodatabase.sql
```

### Notes

1. If update gStore database, must delete with `bin/gdrop weibo` then build again `bin/gbuild weibo ../data.nt`
2. end gserver: `bin/shutdown 12355`