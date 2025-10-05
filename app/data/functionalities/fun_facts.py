import random

class FunFacts:
    FACTS = [
        "🥇 Najwyższa emerytura w Polsce przekracza 40 000 zł miesięcznie! Rekordzista to pan ze Śląska, który nigdy nie był na zwolnieniu lekarskim i pracował ponad 60 lat",
        "🕑 W Polsce średni czas pobierania emerytury to około 20 lat – czyli tyle, co oglądanie całego Netflixa od początku do końca.",
        "🎓 Jeśli zaczynasz pracę w wieku 25 lat i pracujesz do 65., to na emeryturę odkładasz składki przez 480 miesięcy. To jak 480 rat kredytu… tylko że bez banku",
        "📈 Co roku ZUS waloryzuje Twoje składki – w rekordowym roku wskaźnik waloryzacji przekroczył 9%, czyli więcej niż lokata w banku!",
        "🏰 Najstarszy znany polski emeryt mieszkał w Krakowie i dożył ponad 105 lat – jego emerytura trwała dłużej niż niejedna kariera zawodowa.",
        "🚋 Emerytury w Małopolsce są średnio niższe niż na Śląsku – ale za to w Krakowie emeryci mogą jeździć komunikacją miejską z ulgą",
        "👶🏻 Najmłodszy polski emeryt? Funkcjonariusze służb mundurowych mogą przejść na emeryturę nawet po 15 latach służby – czyli szybciej niż niektóre studia doktoranckie!",
        "🎮 Najdłużej pracujący Polak przeszedł na emeryturę po 67 latach pracy – to jakbyś grał w jedną grę wideo od czasów Pegasusa do dzisiejszego PS5",
        "⏳ Pierwsze emerytury w Polsce zaczęto wypłacać w 1934 roku – czyli jeszcze zanim powstała gra Monopoly!",
        "🥳 Rekordzista z Warszawy przeszedł na emeryturę w wieku 99 lat – dopiero gdy uznał, że praca zaczyna być trochę monotonna",
        "📚 Polacy żyją dziś średnio 10 lat dłużej niż ich dziadkowie – więc emerytura to coraz dłuższa „druga kariera",
        "💻 Najmłodsi użytkownicy tego symulatora będą przechodzić na emeryturę około 2060 roku – czyli w epoce, w której może już rządzić sztuczna inteligencja",
        "💾 ZUS przechowuje dane o składkach milionów Polaków – to większy dataset niż niejeden używany w machine learningu",
        "🔮 Według prognoz w 2060 roku stopa zastąpienia spadnie do około 30% – czyli tyle, ile dokładności ma źle wytrenowany model AI",
        "🖥️ Systemy ZUS muszą obsługiwać miliony operacji dziennie – można je porównać do największych baz danych w Polsce.",
        "🔗 Składki emerytalne działają jak blockchain – każdy Twój miesiąc pracy dopisuje nowy „blok” do kapitału."
    ]

    @staticmethod
    def get_random_fact() -> str:
        return random.choice(FunFacts.FACTS)
