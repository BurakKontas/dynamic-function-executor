from utils import print

class Adres:
    sehir: str
    ulke: str
    posta_kodu: int

    def __init__(self, sehir: str, ulke: str, posta_kodu: int):
        self.sehir = sehir
        self.ulke = ulke
        self.posta_kodu = posta_kodu

class Kisi:
    isim: str
    yas: int
    adres: Adres

    def __init__(self, isim: str, yas: int, adres: Adres):
        self.isim = isim
        self.yas = yas
        self.adres = adres

class Sirket:
    sirket_adi: str
    calisanlar: list[Kisi]
    merkez: Adres

    def __init__(self, sirket_adi: str, calisanlar: list[Kisi], merkez: Adres):
        self.sirket_adi = sirket_adi
        self.calisanlar = calisanlar
        self.merkez = merkez

class Urun:
    urun_adi: str
    fiyat: float
    uretici: Sirket

    def __init__(self, urun_adi: str, fiyat: float, uretici: Sirket):
        self.urun_adi = urun_adi
        self.fiyat = fiyat
        self.uretici = uretici

class Siparis:
    siparis_no: int
    musteri: Kisi
    urunler: list[Urun]
    toplam_tutar: float

    def __init__(self, siparis_no: int, musteri: Kisi, urunler: list[Urun], toplam_tutar: float):
        self.siparis_no = siparis_no
        self.musteri = musteri
        self.urunler = urunler
        self.toplam_tutar = toplam_tutar

def siparis_isle(siparis: Siparis, odendi: bool) -> None:
    print(siparis)
    print(type(siparis.musteri))
    print(type(siparis.urunler[0]))
    print(type(siparis.urunler[0].uretici))
    print(f"Sipariş No: {siparis.siparis_no}, Ödendi: {odendi}")