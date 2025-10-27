"""
YAGO Tasks - Görev Tanımları
Her aşama için görevler
"""

from crewai import Task
from typing import Optional


class YagoTasks:
    """YAGO Görev Tanımları"""

    @staticmethod
    def planning_task(agent, project_idea: str) -> Task:
        """
        Planlama Görevi
        Proje fikrini teknik plana dönüştürür

        Args:
            agent: Planlama ajanı
            project_idea: Kullanıcının proje fikri

        Returns:
            Task instance
        """
        return Task(
            description=f"""
            Proje Fikri: "{project_idea}"

            Bu projeyi gerçekleştirmek için:
            1. Teknik gereksinimleri analiz et
            2. Teknoloji yığınını belirle (dil, framework, kütüphaneler)
            3. Proje yapısını tasarla (dosya/dizin yapısı)
            4. Görevleri küçük parçalara böl (epics & user stories)
            5. Kabul kriterlerini belirle

            Çıktı formatı:
            - Markdown formatında teknik plan
            - Açık ve uygulanabilir adımlar
            - Tahmini süre ve zorluk seviyesi
            """,
            expected_output="""
            # Teknik Plan

            ## 1. Genel Bakış
            [Projenin açıklaması]

            ## 2. Teknoloji Yığını
            - Dil: [...]
            - Framework: [...]
            - Kütüphaneler: [...]

            ## 3. Proje Yapısı
            ```
            project/
            ├── src/
            ├── tests/
            └── ...
            ```

            ## 4. Görevler
            ### Epic 1: [...]
            - Story 1.1: [...]
            - Story 1.2: [...]

            ## 5. Kabul Kriterleri
            - [ ] [...]
            """,
            agent=agent,
        )

    @staticmethod
    def coding_task(agent, plan: Optional[str] = None) -> Task:
        """
        Kodlama Görevi
        Plana göre kod yazar

        Args:
            agent: Kodlama ajanı
            plan: Teknik plan (opsiyonel, önceki görevden alınır)

        Returns:
            Task instance
        """
        return Task(
            description=f"""
            Teknik plana dayanarak projeyi kodla:

            1. Proje iskeletini oluştur (dizin yapısı)
            2. Ana modülleri/dosyaları yaz
            3. Her dosya için:
               - Clean code prensipleri uygula
               - Docstring ekle
               - Type hints kullan (Python için)
            4. Gerekli config dosyalarını oluştur
            5. Basit bir kullanım örneği ekle

            ÖNEMLI:
            - Dosya yolu "proje_adi/src/dosya.py" formatında olmalı (workspace/ önceden eklenir)
            - Örnek: path="calculator/src/main.py" (workspace/calculator/src/main.py olarak yazılır)
            - Dosya yazma araçlarını kullan (Dosyaya Yaz)
            - Her dosyayı ayrı ayrı oluştur
            - Test edilebilir kod yaz
            - Maksimum 10-15 dosya oluştur (gerekli olanları)

            {f'Plan: {plan}' if plan else ''}
            """,
            expected_output="""
            Tüm proje dosyaları workspace/ altında oluşturulmuş olmalı:
            - Ana kod dosyaları
            - Config dosyaları
            - requirements.txt veya package.json
            - Basit kullanım örneği

            Her dosya için kısa açıklama
            """,
            agent=agent,
        )

    @staticmethod
    def testing_task(agent) -> Task:
        """
        Test Görevi
        Kod için testler yazar ve çalıştırır

        Args:
            agent: Test ajanı

        Returns:
            Task instance
        """
        return Task(
            description="""
            Yazılan kod için kapsamlı testler oluştur:

            1. workspace/ içindeki kodu incele
            2. Test stratejisi belirle (unit, integration)
            3. Test dosyaları oluştur:
               - tests/ dizini
               - test_*.py dosyaları
               - Her fonksiyon/modül için testler
            4. Testleri çalıştır (pytest)
            5. Sonuçları raporla

            Test Kriterleri:
            - Edge case'leri test et
            - Pozitif ve negatif senaryolar
            - En az %70 code coverage

            Araçlar:
            - Dosya yazma (test dosyaları için)
            - Test çalıştırma komutu
            """,
            expected_output="""
            # Test Raporu

            ## Yazılan Testler
            - test_*.py dosyaları listesi
            - Her test dosyasının amacı

            ## Test Sonuçları
            ```
            [pytest çıktısı]
            ```

            ## Özet
            - Toplam test: X
            - Başarılı: X
            - Başarısız: X
            - Coverage: %XX
            """,
            agent=agent,
        )

    @staticmethod
    def review_task(agent) -> Task:
        """
        Kod İnceleme Görevi
        Kod kalitesini değerlendirir

        Args:
            agent: Kod inceleme ajanı

        Returns:
            Task instance
        """
        return Task(
            description="""
            workspace/ içindeki kodu incele ve raporla:

            1. Kod Kalitesi:
               - Clean code prensipleri
               - DRY (Don't Repeat Yourself)
               - SOLID prensipleri
               - Naming conventions

            2. Güvenlik:
               - Input validation
               - Error handling
               - Sensitive data kontrolü

            3. Best Practices:
               - Dil/framework standartları
               - Code organization
               - Documentation

            4. Öneriler:
               - İyileştirme noktaları
               - Potansiyel bug'lar
               - Performance optimizasyonları

            Araçlar:
            - Dosya okuma
            - Dosya listeleme
            """,
            expected_output="""
            # Kod İnceleme Raporu

            ## Genel Değerlendirme
            - Skor: X/10
            - Durum: [İyi/Orta/Zayıf]

            ## Bulgular

            ### ✅ İyi Yanlar
            - [...]

            ### ⚠️ Dikkat Edilmesi Gerekenler
            - [...]

            ### ❌ Kritik Sorunlar
            - [...]

            ## Öneriler
            1. [...]
            2. [...]

            ## Sonuç
            [Genel yorum ve öneriler]
            """,
            agent=agent,
        )

    @staticmethod
    def documentation_task(agent) -> Task:
        """
        Dokümantasyon Görevi
        README ve dokümanlar oluşturur

        Args:
            agent: Dokümantasyon ajanı

        Returns:
            Task instance
        """
        return Task(
            description="""
            Proje için kapsamlı dokümantasyon oluştur:

            1. README.md:
               - Proje açıklaması
               - Kurulum adımları
               - Kullanım örnekleri
               - API referansı (varsa)
               - Katkıda bulunma rehberi

            2. Kod Dokümantasyonu:
               - Her dosyanın amacı
               - Fonksiyon/sınıf açıklamaları
               - Parametreler ve dönüş değerleri

            3. Diyagramlar (Mermaid):
               - Mimari diyagram
               - Akış diyagramları (gerekirse)

            Araçlar:
            - Dosya okuma (kodu incelemek için)
            - Dosya yazma (README.md)
            """,
            expected_output="""
            workspace/ dizininde:
            - README.md (kapsamlı ve profesyonel)
            - CONTRIBUTING.md (opsiyonel)
            - API.md (eğer API varsa)

            Her dosya markdown formatında, anlaşılır ve örneklerle zenginleştirilmiş
            """,
            agent=agent,
        )
