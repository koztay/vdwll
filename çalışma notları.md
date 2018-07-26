#### Ubuntu Mate 'de import gi çalışmıyor. O nedenle Gtk3+ kurmak lazım aşağıdaki komutla kuruyoruz:

```
sudo apt-get install libgtk-3-dev
```

#### export DISPLAY=:0 komutu ile ssh ile bağlanıp GUI program çalıştırılabiliyor.

#### supervisor ile otomatik çalıştırmada aşağıdaki hata :

```
Xlib.error.XauthError: ~/.Xauthority: [Errno 2] No such file or directory:
```
bunun çözümü için :
 
 ```
 $ touch ~/.Xauthority
 ```
 
 ayrıca diğer ayarları da yapmışsan o zaman supervisor ile açılıyır program.
 
 