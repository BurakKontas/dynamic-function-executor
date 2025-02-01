import json

class Adres:
    sehir: str
    ulke: str
    posta_kodu: int

    def __init__(self, sehir: str, ulke: str, posta_kodu: int):
        self.sehir = sehir
        self.ulke = ulke
        self.posta_kodu = posta_kodu

    def to_dict(self):
        return self.__dict__

    def __repr__(self):
        return json.dumps(self.to_dict(), indent=4, ensure_ascii=False)

class Kisi:
    isim: str
    yas: int
    adres: Adres

    def __init__(self, isim: str, yas: int, adres: Adres):
        self.isim = isim
        self.yas = yas
        self.adres = adres

    def to_dict(self):
        return {
            "isim": self.isim,
            "yas": self.yas,
            "adres": self.adres.to_dict()
        }

    def __repr__(self):
        return json.dumps(self.to_dict(), indent=4, ensure_ascii=False)

class Sirket:
    sirket_adi: str
    calisanlar: list[Kisi]
    merkez: Adres

    def __init__(self, sirket_adi: str, calisanlar: list[Kisi], merkez: Adres):
        self.sirket_adi = sirket_adi
        self.calisanlar = calisanlar
        self.merkez = merkez

    def to_dict(self):
        return {
            "sirket_adi": self.sirket_adi,
            "calisanlar": [kisi.to_dict() for kisi in self.calisanlar],
            "merkez": self.merkez.to_dict()
        }

    def __repr__(self):
        return json.dumps(self.to_dict(), indent=4, ensure_ascii=False)

class Urun:
    urun_adi: str
    fiyat: float
    uretici: Sirket

    def __init__(self, urun_adi: str, fiyat: float, uretici: Sirket):
        self.urun_adi = urun_adi
        self.fiyat = fiyat
        self.uretici = uretici

    def to_dict(self):
        return {
            "urun_adi": self.urun_adi,
            "fiyat": self.fiyat,
            "uretici": self.uretici.to_dict()
        }

    def __repr__(self):
        return json.dumps(self.to_dict(), indent=4, ensure_ascii=False)

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

    def to_dict(self):
        return {
            "siparis_no": self.siparis_no,
            "musteri": self.musteri.to_dict(),
            "urunler": [urun.to_dict() for urun in self.urunler],
            "toplam_tutar": self.toplam_tutar
        }

    def __repr__(self):
        return json.dumps(self.to_dict(), indent=4, ensure_ascii=False)

def siparis_isle(siparis: Siparis, odendi: bool):
    return siparis, odendi


# settings = {
#     "name": "Sipariş İşleme",
#     "enabled": True,
#     "description": "Örnek bir sipariş işleme fonksiyonu.",
# }