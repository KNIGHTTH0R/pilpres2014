pilpres2014
===========

Pilpres 2014 KPU C1 DA1 DB1 Data Scrapper
<code>
 python pilpres.py --tipe c1
 return: prop,prop_id,kab,kab_id,kec,kec_id,kel,kel_id,tps_id,kode_file_c1_ke_N

 python pilpres.py --tipe c1 --download
 -> download seluruh file c1 menggunakan wget (run in background). rawan cpu usage :P

 python pilpres.py --tipe c1 --download --nowget
 -> download seluruh file c1 via urllib standar. prosesnya lebih lama.

 python pilpres.py --tipe c1 --list-only
 -> return list of http://scanc1.kpu.go.id/viewp.php?f=<kode_file_c1_keN>.jpg

 python pilpres.py --tipe c1 --nogambar
 return: prop,prop_id,kab,kab_id,kec,kec_id,kel,kel_id

 python pilpres.py --tipe da1
 return: prop,prop_id,kab,kab_id,kec,kec_id,capres-cawapres,kel,nilai

 python pilpres.py --tipe db1
 return: prop,prop_id,kab,kab_id,capres-cawapres,kec,nilai

 note: nilai -1 = data belum tersedia (DA1 & DB1)

 python pilpres.py --prop <prop_id> --kab <kab_id> --kec <kec_id> --kel <kel_id> --resume
 -> memulai proses crawl dari spesifik propinsi, kabupaten, kecamatan, atau kelurahan

 python pilpres.py --prop <prop_id> --kab <kab_id> --kec <kec_id> --kel <kel_id>
 -> memperkecil area crawl di spesifik propinsi, kabupaten, kecamatan, dan kelurahan saja

 python pilpres.py --save
 -> menyimpan hasil crawl ke separated files di bawah folder crawl_*. default hanya stdout.

 python pilpres.py --file <nama_file.txt>
 -> menyimpan hasil crawl ke spesifik file
</code>
