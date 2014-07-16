# Pilpres 2014 KPU C1, DA1, DB1 Scraper
# 
# python pilpres.py --tipe c1
# return: prop,prop_id,kab,kab_id,kec,kec_id,kel,kel_id,tps_id,kode_file_c1_ke_N
#
# python pilpres.py --tipe c1 --download
# -> download seluruh file c1 menggunakan wget (run in background). rawan cpu usage :P
#
# python pilpres.py --tipe c1 --download --nowget
# -> download seluruh file c1 via urllib standar. prosesnya lebih lama.
#
# python pilpres.py --tipe c1 --list-only
# -> return list of http://scanc1.kpu.go.id/viewp.php?f=<kode_file_c1_keN>.jpg
#
# python pilpres.py --tipe c1 --nogambar
# return: prop,prop_id,kab,kab_id,kec,kec_id,kel,kel_id
#
# python pilpres.py --tipe da1
# return: prop,prop_id,kab,kab_id,kec,kec_id,capres-cawapres,kel,nilai
#
# python pilpres.py --tipe db1
# return: prop,prop_id,kab,kab_id,capres-cawapres,kec,nilai
#
# note: nilai -1 = data belum tersedia (DA1 & DB1)
#
# python pilpres.py --prop <prop_id> --kab <kab_id> --kec <kec_id> --kel <kel_id> --resume
# -> memulai proses crawl dari spesifik propinsi, kabupaten, kecamatan, atau kelurahan
#
# python pilpres.py --prop <prop_id> --kab <kab_id> --kec <kec_id> --kel <kel_id>
# -> memperkecil area crawl di spesifik propinsi, kabupaten, kecamatan, dan kelurahan saja
#
# python pilpres.py --save
# -> menyimpan hasil crawl ke separated files di bawah folder crawl_*. default hanya stdout.
#
# python pilpres.py --file <nama_file.txt>
# -> menyimpan hasil crawl ke spesifik file


import BeautifulSoup
import urllib2
import sys, subprocess
import time
import socket
socket.setdefaulttimeout(5)


class Pilpres:
  def __init__(self):
    self.runcode = "crawl_" + str(int(time.time())) # identifier aja, biar support resume crawl
    self.url = "http://pilpres2014.kpu.go.id/"
    self.only = True
    self.save = False
    self.include_gambar = True
    self.download = False
    self.list_only = False
    self.file = None
    self.wget = True
    self.mkdir = False
    self.tipe = "c1" # pilihannya cuman c1 or da1 or db1

  def buka(self, url,n=0):
    try:
      req = urllib2.Request(url, headers={ 'User-Agent': 'Mozilla/5.0/@judotens/pilpres2014' })
      uri = urllib2.urlopen(req)
      chunk = uri.read()  
    except Exception as err:
      if str(err).find("503") > -1 and n < 3:
        time.sleep(3)
        return self.buka(url, n+1)
      else:
        if n < 3:
          time.sleep(3)
          return self.buka(url, n+1)
        else:
          print "ERROR:", str(url), str(err)
          sys.exit()

    return chunk

  def parse_option(self, html):
    # parsing option jadi array
    soup = BeautifulSoup.BeautifulSoup(html)
    form = soup.find("div", {'class': 'form'})
    if form == None: return False

    rows = form.findAll("option")
    area = []
    for r in rows:
      if r['value'] != "":
        area.append( (r.text, str(r['value'])) )
    return area

  def parse_gambar(self, html):
    # parsing table gambar jadi array
    soup = BeautifulSoup.BeautifulSoup(html)
    tps = soup.find("div", {'id': 'daftartps'})
    if not tps: return False
    gambars = []
    rows = tps.findAll("tr")
    for row in rows:
      tds = row.findAll("td")
      if len(tds) > 1:
        gbrs = row.findAll("a", {'class': 'image1_aktif'})
        i_gambars = []
        for gbr in gbrs:
          gbr_id = gbr['href'].replace("javascript:read_jpg('", "").replace("')", "")
          if gbr_id != None: i_gambars.append(str(gbr_id))

        gambars.append((tds[1].text, i_gambars))

    return gambars

  def parse_table(self, html):
    # parsing table rekap jadi angka, cuman ngambil data dari table paling terakhir: jumlah suara sah per kontenstan / area
    soup = BeautifulSoup.BeautifulSoup(html)
    try: table_kel = soup.findAll("table")[1].findAll("tr")[2].findAll("th")
    except: return False

    # bebersih dikit lah, header sama footer row
    table_kel.pop(0)
    table_kel.pop(0)
    table_kel.pop(len(table_kel)-1)


    # parsing areanya dulu
    kelurahans = []
    for row in table_kel: kelurahans.append(row.text)

    prabowo_hatta = []
    jokowi_jk = []

    # mulai parsing angka, kalo datanya belum ada dia return -1
    table_prabowo = soup.findAll("table")[2].findAll("tr")[3].findAll("td")
    table_prabowo.pop(0)
    table_prabowo.pop(0)

    for row in table_prabowo:
      try: prabowo_hatta.append(int(row.text))
      except: prabowo_hatta.append(-1)


    table_jokowi = soup.findAll("table")[2].findAll("tr")[4].findAll("td")
    table_jokowi.pop(0)
    table_jokowi.pop(0)

    for row in table_jokowi:
      try: jokowi_jk.append(int(row.text))
      except: jokowi_jk.append(-1)

    # mulai rapihin lahh
    buffers = []
    for n in range(0, len(kelurahans)):
      try: item = ( "prabowo-hatta", kelurahans[n], str(int(prabowo_hatta[n])) )
      except: item = ( "prabowo-hatta", kelurahans[n], "-1" )
      buffers.append(item)

      try: item = ( "jokowi-jk", kelurahans[n], str(int(jokowi_jk[n])) )
      except: item = ( "jokowi-jk", kelurahans[n], "-1" )
      buffers.append(item)

    return None, None, None, None, buffers

  # rakit target url based on tipe
  def render_url(self, grandparent, parent): return self.url + self.tipe + ".php?cmd=select&grandparent=" + str(grandparent) + "&parent=" + str(parent)

  def jelajah(self, mulai=True, prop=None, kab=None, kec=None, kel=None):
    # cari modal awal dulu, list propinsi
    awal = self.buka(self.url + self.tipe + ".php")
    propinsis = self.parse_option(awal)

    for propinsi in propinsis:
      # skip kalo belon masuk ke propinsi yg diset user
      if prop and not mulai and propinsi[1] != prop: continue

      html = self.buka(self.render_url(0, propinsi[1]))
      kabupatens = self.parse_option(html)
      for kabupaten in kabupatens:
        # skip kalo belon masuk ke kabupaten yg diset user
        if kab and not mulai and kabupaten[1] != kab: continue

        html = self.buka(self.render_url(propinsi[1], kabupaten[1]))

        # handle parsingan utk db1
        if self.tipe == "db1":
          # klo user gak mau crawl di specific loc, maka lanjutkan perjalananmu nak!
          if not self.only: mulai = True
          arrays = self.parse_table(html)

          item = propinsi, kabupaten, ("-","-"), ("-","-"), arrays
          self.cetak(item)

        else:
          kecamatans = self.parse_option(html)
          for kecamatan in kecamatans:
            # skip kalo belon masuk ke kecamatan yg diset user
            if kec and not mulai and kecamatan[1] != kec: continue

            html = self.buka(self.render_url(kabupaten[1], kecamatan[1]))

            # handle parsingan utk da1
            if self.tipe == "da1":
              # klo user gak mau crawl di specific loc, maka lanjutkan perjalananmu nak!
              if not self.only: mulai = True
              arrays = self.parse_table(html)
              item = propinsi, kabupaten, kecamatan, ("-","-"), arrays
              self.cetak(item)

            else:
              kelurahans = self.parse_option(html)
              for kelurahan in kelurahans:
                # skip kalo belon masuk ke kelurahan yg diset user
                if kel and not mulai and kelurahan[1] != kel: continue
                else: mulai = True

                # handle parsingan utk c1
                if self.tipe == "c1":
                  arrays = []
                  if self.include_gambar:
                    html = self.buka(self.render_url(kecamatan[1], kelurahan[1]))
                    arrays = self.parse_gambar(html)

                  item = propinsi, kabupaten, kecamatan, kelurahan, arrays
                  self.cetak(item)

                # udahan klo user ngeset cuma ke specific kel
                if kel and self.only: return True

            # udahan klo user ngeset cuma ke specific kec
            if kec and not kel and self.only: return True

          # udahan klo user ngeset cuma ke specific kab
          if kab and not kel and not kec and self.only: return True

      # udahan klo user ngeset cuma ke specific prop
      if prop and not kab and not kel and not kec and self.only: return True
    
  def cetak(self, item):

    propinsi, kabupaten, kecamatan, kelurahan, arrays = item

    # create temp dir utk store result
    if (self.save or self.download) and not self.mkdir:
      try:
        tmp = subprocess.Popen("mkdir " + str(self.runcode), shell=True)
        tmp.wait()
        self.mkdir = True
      except: pass

    # specify penamaan file based on user options
    if self.file: fp = open(self.file, "a")
    if self.save:
      bread = [self.tipe, propinsi[0]]
      if self.tipe == "da1": bread += [kabupaten[0], kecamatan[0]]
      if self.tipe == "db1": bread.append(kabupaten[0])
      if self.tipe == "c1" and self.only:
        try:
          if kabupaten[0][0] != "-": bread.append(kabupaten[0])
          #if kecamatan[0][0] != "-": bread.append(kecamatan[0])
        except: pass

      fp = open(str(self.runcode) + "/" + "-".join(bread).lower().replace(" ", "_").replace("-.","").replace("--","") + ".tsv", "a")

    # handling cetakan c1
    if self.tipe == "c1":
      # handle cetakan standar, agak irit
      if not self.include_gambar:
        try:
          baris = "%s\t%s\t%s\t%s" % ("\t".join(propinsi), "\t".join(kabupaten), "\t".join(kecamatan), "\t".join(kelurahan))
          if self.save or self.file: fp.write(baris + "\n")
          print baris
        except Exception as err:
          #print "ERROR", str(err)
          pass

      else:
        # khusus utk keluarin list gambar, lebih mahal 1 panggilan/kelurahan
        for gambar in arrays:
          try:
            baris = "%s\t%s\t%s\t%s\t%s\t%s" % ("\t".join(propinsi), "\t".join(kabupaten), "\t".join(kecamatan), "\t".join(kelurahan), gambar[0], "\t".join(gambar[1]))
            if self.save or self.file: fp.write(baris + "\n")
            if not self.list_only: print baris

            # handle dongdot gambar
            if self.download or self.list_only:
              for g in gambar[1]:
            
                target = "http://scanc1.kpu.go.id/viewp.php?f=" + str(g) + ".jpg"
                nama_file = "%s_%s_%s_%s_%s_%s.jpg" % ( str(propinsi[1]), str(kabupaten[1]), str(kecamatan[1]), str(kelurahan[1]), str(gambar[0]), str(g))

                if self.list_only:
                  # cetak list of url gambar aja, tanpa ket prop/kab/kec/kel dan tanpa donlot
                  print target
                  if self.save or self.file: fp.write(baris + "\n")
                else:
                  if self.wget:
                    # download run in background aja lah pake wget
                    tmp = subprocess.Popen("nohup wget \"" + str(target) + "\" -O " + str(self.runcode) + "/" + str(nama_file) + " > /dev/null &", shell=True)
                  else:
                    # download pake cara biasa. lama dahhh
                    try:
                      konten = self.buka(target)
                      open(str(self.runcode) + "/" + nama_file, "w").write(konten)
                    except: continue

          except: continue

    # handle cetakan utk db1 dan db2
    if self.tipe == "db1" or self.tipe == "da1":
      for array in arrays:
        if not array: continue
        for ar in array:
          try:
            baris = "%s\t%s\t%s\t%s\t%s" % ("\t".join(propinsi), "\t".join(kabupaten), "\t".join(kecamatan), "\t".join(kelurahan), "\t".join(ar))
            baris = baris.replace("\t-\t-", "") # bersihin - - buat yg null
            if self.save or self.file: fp.write(baris + "\n")
            print baris
          except Exception as err:
            #print "ERROR", str(err)
            pass

    if self.save or self.file:
      try: fp.close()
      except: pass

if __name__ == "__main__":
  import sys, getopt

  pilpres = Pilpres()

  try:
    opts, args = getopt.getopt(sys.argv[1:],"p:b:c:l:smgdf:r:t:wl",["prop=","kab=", "kec=", "kel=", "save", "resume", "nogambar", "download", "file=", "runcode=", "tipe=","nowget","list-only"])
  except getopt.GetoptError:
      opts = [('-h', '--help')]

  mulai, prop, kab, kec, kel = True, None, None, None, None
  for opt, arg in opts:
      if opt == '-h':
        isi = open(sys.argv[0]).read().replace("#","").split("\n")
        print "\n".join(isi[:37])
        sys.exit()
      elif opt in ("-p", "--prop"):
        # set crawl ke specific propinsi
        prop = arg
      elif opt in ("-b", "--kab"):
        # set crawl ke specific kabupaten
        kab = arg
      elif opt in ("-c", "--kec"):
        # set crawl ke specific kecamatan
        kec = arg
      elif opt in ("-l", "--kel"):
        # set crawl ke specific kelurahan
        kel = arg
      elif opt in ("-f", "--file"):
        # set hasil crawl ke specific file
        pilpres.file = arg
        # kosongin isi file dulu
        try: open(pilpres.file, "w").write("")
        except: pass
      elif opt in ("-m", "--resume"):
        # set agar crawl cuma ke specific prop/kab/kec/kel
        pilpres.only = False
      elif opt in ("-s", "--save"):
        # set agar crawler ngesave hasil pencarian ke file. not in stdout only
        pilpres.save = True
      elif opt in ("-r", "--runcode"):
        # set identifier agar crawler ngesave hasil ke specific folder (bisa utk resume last crawl runcode)
        pilpres.runcode = arg
      elif opt in ("-t", "--tipe"):
        # tipe data yg dipilih utk dicrawl. default: c1
        if str(arg).lower() in ["c1", "da1", "db1"]: pilpres.tipe = str(arg).lower()
        else:
          print "-> Tipe yg disupport: c1, da1, atau db1"
          sys.exit()


      # additional option utk tipe c1
      elif opt in ("-g", "--nogambar"):
        # set cetakan tanpa list kode file c1
        pilpres.include_gambar = False
      elif opt in ("-d", "--download"):
        # set agar crawler ikut download file c1. klo --nogambar diset, download disabled
        pilpres.download = True
      elif opt in ("-l", "--list-only"):
        # set agar crawler cuma nyetak list of url gambar form c1, tanpa didonlot
        pilpres.list_only = True

      elif opt in ("-w", "--nowget"):
        # set agar download via standar urllib instead wget
        pilpres.wget = False



  if prop or kab or kec or kel: mulai = False
  pilpres.jelajah(mulai=mulai, prop=prop, kab=kab, kec=kec, kel=kel)
  
    
