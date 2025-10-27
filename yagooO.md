İstediğiniz gibi YAGO – Yerel AI Geliştirme Orkestratörü için kapsamlı, A’dan Z’ye teknik dokümantasyonu aşağıda tek parça halinde sunuyorum. Belge; proje vizyonu, mimari, gereksinimler, kurulum, örnek kod iskeleti, test/kalite ve güvenlik dahil uçtan uca tüm detayları içerir. Temel kavramsal tasarım ve faz planı için hazırladığınız çekirdek dokümana, pratik kurulum ve örnek kod iskeleti için de uygulama odaklı notlarınıza dayandım. 

yago

 

yagoO

YAGO – Yerel AI Geliştirme Orkestratörü

Sürüm: 1.0 (Teknik Tasarım)
Tarih: 25 Ekim 2025
Hedef Platform: Apple Silicon (M4 Max odaklı; lokal çalışma)

0) Yönetici Özeti

YAGO, proje fikirlerinden başlayarak dokümantasyon üretme, kod yazma, test, inceleme ve raporlama adımlarını çok ajanlı bir mimariyle lokalde (internet erişimi gerektirmeden) otomatikleştirmeyi hedefler. Orkestratör AI, Planlama/Kodlama/Test/İnceleme/Döküman gibi uzman ajansları koordine eder; Git, dosya sistemi, test çatıları ve (opsiyonel) vektör veritabanı ile etkileşir. Bu yaklaşım, tek geliştiricinin verimini ölçekler; ancak ajan koordinasyonu, model yetenekleri ve kalite kontrol başlıca zorluklardır. Kavramsal kapsam ve faz planı özgün projenizde detaylı tanımlanmıştır. 

yago

1) Kapsam, Hedefler ve Başarı Kriterleri

Kapsam:

Fikir → Plan → Dokümantasyon → Kod → Test → Kod İnceleme → Raporlama → (İsteğe bağlı) Paketleme/Dağıtım uçtan uca lokal akış. 

yago

Ajanlar: Planlama, Kodlama, Test, Kod İnceleme, Dokümantasyon (gerektikçe genişletilebilir). 

yago

Hedefler:

Aynı makinede birden çok LLM (veya uzman modeller) ile işbirliği.

Dosya sistemi/Git/test araçlarına güvenli ve sınırlı erişim.

Tek komutla “uçtan uca” örnek proje üretimi. 

yagoO

Başarı Kriterleri (MVP):

Komut satırından tek bir fikir metnini alıp, README + temel proje iskeleti + çalışan test üreten prototip.

Tüm üretilen artefaktlar workspace/ altında versiyonlanmış halde. 

yagoO

2) Terminoloji ve Varsayımlar

Orkestratör AI: Ajanlar arası koordinasyon ve iş akışı kontrolü.

Uzman Ajanlar: Belirli rol (Planlama/Kod/Test/İnceleme/Dokümantasyon) için optimize edilmiş ajan süreçleri. 

yago

Lokal LLM Çalıştırma Motoru: Ollama/LM Studio benzeri, Apple Silicon için optimize. 

yago

Ajan Framework: CrewAI/AutoGen/LangChain tabanlı; bu dokümanda örnekler CrewAI + Ollama ile verilmiştir. 

yagoO

3) Mimari Genel Bakış
3.1. Mantıksal Mimari
graph TD
    UI[Kullanıcı Arayüzü / CLI] --> ORCH(Orkestratör AI)
    ORCH --> PLAN[Planlama Ajanı]
    ORCH --> DOCS[Dokümantasyon Ajanı]
    ORCH --> CODE[Kodlama Ajanı]
    ORCH --> TEST[Test Ajanı]
    ORCH --> REVIEW[Kod İnceleme Ajanı]

    CODE --> FS[(Dosya Sistemi)]
    TEST --> FS
    DOCS --> FS
    CODE --> GIT[(Git)]
    TEST --> GIT
    REVIEW --> GIT

    subgraph Altyapı
    LLM[Lokal LLM Motoru (Ollama)]
    VDB[(Vektör DB - Opsiyonel)]
    end

    ORCH --> LLM
    PLAN --> LLM
    CODE --> LLM
    TEST --> LLM
    REVIEW --> LLM
    DOCS --> LLM
    PLAN --> VDB


Bu yapı, kavramsal tasarımınızdaki modüler ve olay güdümlü yaklaşımı izler. 

yago

3.2. Uçtan Uca İş Akışı (Özet)

Girdi: Kullanıcı bir fikir/gereksinim tanımlar (CLI).

Planlama: Planlama Ajanı epik/story ve teknoloji yığını çıkarır.

Dokümantasyon (1): İlk teknik döküman/README taslağı.

Kodlama: Proje iskeleti ve temel modüller üretilir, Git’e işlenir.

Test: Unit/integ testler oluşturulur ve koşturulur.

İnceleme: Statik analiz/standartlara uyum ve PR notları.

Dokümantasyon (2): API/arch diyagramları güncellenir.

Raporlama: Özet, başarısızlıklar ve öneriler. 

yago

4) Bileşenler
4.1. Orkestratör

Görev kırılımı, ajan atamaları, hata/geri bildirim döngüleri, durumsal raporlama.

Basit MVP’de sequential akış; ileride hierarchical (yönetici ajan) ve koşullu dallanmalar. 

yago

 

yagoO

4.2. Uzman Ajanlar

Planlama: Gereksinim → mimari/epic/story planı.

Dokümantasyon: Plan ve koda göre README, API referansı, diyagram üretimi.

Kodlama: Dil/framework odaklı kod üretimi, refactor, dosya/terminal araçları kullanımı.

Test: Pytest/Jest vb. entegrasyon; sonuçları parse etme, raporlama.

Kod İnceleme: Best practice, güvenlik (statik analiz), okunabilirlik bulguları. 

yago

4.3. Araçlar ve Entegrasyonlar

Dosya/Terminal Araçları: workspace/ ile sınırlı, güvenli yazma/okuma ve komut koşturma.

Git: Branch/commit/merge akışları, otomatik mesaj formatları.

Lokal LLM: Ollama (llama3, codellama, deepseek-coder vb. seçilebilir).

Vektör DB (ops.): Proje bağlamı ve geri getirim (RAG). 

yago

 

yagoO

5) Gereksinimler
5.1. Donanım

Apple Silicon (M4 Max önerilir), ≥64 GB RAM (128 GB+ daha iyi), hızlı SSD (≥1 TB). 

yago

5.2. Yazılım

macOS (Sonoma+), Python 3.10+, Docker Desktop, Git.

Ollama/LM Studio, CrewAI, LangChain ekosistemi, test çatıları (Pytest/Jest). 

yago

 

yagoO

5.3. İşlevsel Gereksinimler

CLI’dan fikir alıp temel ürün artefaktları üretme.

Ajanların dosya/terminal erişimi yalnızca workspace/ içinde.

Testler başarısızsa akış döngüye girip düzeltme görevi üretmeli (MVP’de manuel onay kabul edilebilir). 

yagoO

5.4. NFR (Performans/Güvenilirlik/İzlenebilirlik)

Tek fikir için uçtan uca akış tek makinede tamamlanır.

Tüm adımlar loglanır, artefaktlar Git ile izlenir.

Hata durumunda tekrar edilebilirlik ve kısmi/artan çalıştırma. 

yago

6) Kurulum ve Konfigürasyon
6.1. Ortam

Python sanal ortam ve bağımlılıklar:

python3 -m venv yago_env
source yago_env/bin/activate
pip install crewai crewai-tools langchain-community


Ollama kurulumu ve model çekimi (örnek):

# Planlama/Düşünme için
ollama pull llama3:8b
# Kodlama için (RAM durumuna göre)
ollama pull deepseek-coder:33b  # veya codellama:34b


Model farklılaştırması ve seçimi, pratik önerilerinizle uyumludur. 

yagoO

6.2. Proje İskeleti
yago/
├─ workspace/                # Ajanların yalnızca burada çalışmasına izin verilir
├─ agents.py                 # Ajan tanımları (planner/coder/tester/reviewer/docs)
├─ tasks.py                  # Görev tanımları
├─ tools.py                  # Dosya/terminal araçları (workspace sandbox)
├─ main.py                   # Orkestrasyonu başlatır
├─ yago.config.yaml          # Konfigürasyon (modeller, sınırlar, politika)
└─ README.md


Bu yapı, pratik örneklerinizle birebir uyumlu bir başlangıç sağlar. 

yagoO

6.3. Örnek yago.config.yaml
llms:
  planner: "llama3:8b"
  coder: "deepseek-coder:33b"
  tester: "llama3:8b"
  reviewer: "llama3:8b"
  docs: "llama3:8b"
sandbox:
  workspace_dir: "./workspace"
  allow_shell: true
  blocked_commands:
    - "rm -rf /"
    - "sudo"
git:
  enable: true
  branch_strategy: "feature-per-task"
  commit_format: "feat(yago): {task_id} - {summary}"
tests:
  runner: "pytest"
  fail_policy: "loop-to-coder"
logging:
  level: "INFO"

7) Örnek Kod İskeleti (Kısaltılmış)
7.1. Araçlar – tools.py
# tools.py
import os, subprocess
from crewai_tools import tool

WORKSPACE_DIR = "./workspace"

class FileTools:
    @tool("Dosyaya Yaz")
    def write_file(path: str, content: str) -> str:
        full_path = os.path.join(WORKSPACE_DIR, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(content)
        return f"Wrote: {full_path}"

    @tool("Dosyayı Oku")
    def read_file(path: str) -> str:
        full_path = os.path.join(WORKSPACE_DIR, path)
        with open(full_path, 'r') as f:
            return f.read()

class TerminalTools:
    @tool("Komut Çalıştır")
    def run_command(command: str) -> str:
        res = subprocess.run(command, shell=True, cwd=WORKSPACE_DIR,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return f"OUT:\n{res.stdout}\nERR:\n{res.stderr}"


Araçların yalnızca workspace/ altında çalışacak şekilde sınırlandırılması güvenlik için kritiktir. 

yagoO

7.2. Ajanlar – agents.py
# agents.py
from crewai import Agent
from langchain_community.llms import Ollama
from tools import FileTools, TerminalTools

llm_planner = Ollama(model="llama3:8b")
llm_coder = Ollama(model="deepseek-coder:33b")

file_tools = FileTools()
term_tools = TerminalTools()

class YagoAgents:
    def planner(self):
        return Agent(role='Mimar & PM',
                     goal='Gereksinimleri teknik plana dönüştür.',
                     backstory='Büyük projeleri parçalara ayırırsın.',
                     verbose=True, llm=llm_planner)

    def coder(self):
        return Agent(role='Kıdemli Geliştirici',
                     goal='Plana göre kodu yaz ve kaydet.',
                     backstory='Temiz ve test edilebilir kod yazarsın.',
                     verbose=True, llm=llm_coder,
                     tools=[file_tools.write_file, file_tools.read_file, term_tools.run_command])


Ajan-LLM eşleşmesi ve araç kullanımı için pratik önerileriniz temel alınmıştır. 

yagoO

7.3. Görevler – tasks.py
# tasks.py
from crewai import Task

class YagoTasks:
    def planning(self, agent, idea: str):
        return Task(
          description=f"Fikir: '{idea}'. Mimariyi ve görev listesini çıkar.",
          expected_output="Teknik plan + epics/user stories",
          agent=agent)

    def coding(self, agent):
        return Task(
          description="Plana dayanarak proje iskeleti ve ana modülleri oluştur. "
                      "Kodları workspace'e yaz ve basit test ekle.",
          expected_output="Çalışan proje iskeleti + testler",
          agent=agent)

7.4. Orkestrasyon – main.py
# main.py
import os
from crewai import Crew, Process
from agents import YagoAgents
from tasks import YagoTasks

os.environ["OPENAI_API_KEY"] = "NA"  # Yerel çalışıyoruz

agents = YagoAgents()
tasks = YagoTasks()

planner = agents.planner()
coder   = agents.coder()

idea = "Flask ile tek endpoint: {'message': 'Merhaba Dünya'} döndür."
t_plan = tasks.planning(planner, idea)
t_code = tasks.coding(coder)

crew = Crew(agents=[planner, coder], tasks=[t_plan, t_code],
            verbose=2, process=Process.sequential)

print("YAGO başlatılıyor...")
result = crew.kickoff()
print("Tamamlandı.\n", result)


Bu iskelet, MVP’yi ayağa kaldırmak için önerdiğiniz akışla birebir uyumludur. 

yagoO

8) Test, Kalite ve İnceleme
8.1. Test Stratejisi

Birim Testleri (pytest) ve örnek entegrasyon testi (Flask endpoint).

Ajan üretimli test iskeleti; başarısızlıkta Kodlama Ajanına “düzeltme” görevi.

Hedef: Kırmızı → Yeşil döngüsünü otomatikleştirmek. 

yago

8.2. Kod İnceleme

Statik analiz (ruff/flake8), basit güvenlik taramaları, stil denetimi.

“İnceleme raporu” artefaktı ve Git yorumları. 

yago

8.3. Kalite Kapıları

Test başarısızsa merge yok.

README ve temel mimari diyagram güncellenmeden sürüm yükseltme yok. 

yago

9) Güvenlik, İzolasyon ve Politika

Sandbox: Yalnızca workspace/ erişimi; tehlikeli komutların kara listesi.

İzinli Araçlar: Dosya/terminal/Git çağrılarında komut beyaz-listesi.

Model Sızıntısı: Lokal çalıştığı için kod/veri dışarı çıkmaz (politikayla garanti altına alın).

Günlükleme: Komut/araç çağrıları, dosya yazımları ve Git aktiviteleri izlenir. 

yagoO

10) İşletim, Loglama ve Gözlemlenebilirlik

Log Seviyeleri: DEBUG/INFO/WARN/ERROR; ajan başına korelasyon kimliği.

Artefaktlar: /workspace, Git geçmişi ve test raporları.

Hata Yönetimi: Yakalanan istisnalar için öneri mesajları ve yeniden deneme politikaları. 

yago

11) Riskler ve Azaltımlar

Model Yetenek Sınırları: Küçük/orta modellerin karmaşık projelerde zorlanması → görevleri daha küçük parçalara böl, görev-özel prompt şablonları kullan. 

yago

Kaynak Tüketimi: Birden çok LLM paralelliği RAM/GPU sınırlarını zorlayabilir → sıralı akış, quantization, micro-batching. 

yago

Koordinasyon Karmaşıklığı: Ajanlar arası bağımlılıklar → basitten başla, hiyerarşik sürece kademeli geç. 

yago

Kalite Güvencesi: Halüsinasyon/yanlış kod → test/inceleme kapıları ve manuel onay noktaları. 

yago

12) Yol Haritası (Fazlar)

Faz 1: Model araştırması ve kurulum; 1–2 model testleri.

Faz 2: Orkestratör + 2 ajan (Planlama/Kodlama) prototipi.

Faz 3: Test/İnceleme/Dokümantasyon ajanlarının eklenmesi.

Faz 4: Git/FS/Test entegrasyonları; uçtan uca demo.

Faz 5: İyileştirme/optimizasyon ve (ops.) minimal Web UI.
Bu plan, sizin hazırladığınız faz zamanlamaları ve çıktı tanımlarıyla uyumludur. 

yago

13) Geliştirme Standartları

Branching: main korumalı, feature/* dalları.

Commit Mesajları: Conventional Commits (örn. feat(yago): plan taslağı).

Kod Stili: PEP8 + ruff; otomatik format (black).

Dokümantasyon: Her özellik PR’ı README/CHANGELOG güncellemesiyle. 

yago

14) CLI Kullanım Örneği
# Sanal ortam ve servisler aktif kabul edilmiştir
python main.py \
  --idea "Flask ile /hello endpoint'i ve {'message': 'Merhaba Dünya'} yanıtı" \
  --plan-out workspace/PLAN.md \
  --readme-out workspace/README.md


MVP’de parametreler sabit olabilir; ileride YAML tabanlı konfigürasyona geçilir. 

yagoO

15) Ajan İletişim Protokolü (Öneri)

Mesaj Şeması: {role, task_id, input, context, tools_allowed, output_expectation, artifacts}

Durumlar: READY → RUNNING → BLOCKED/WAITING → DONE/FAILED

Geri Bildirim Döngüsü: Test/İnceleme “FAILED” ise Orkestratör → Kodlama’ya “FIX” görevi. 

yago

16) Diyagramlar ve Dökümantasyon Üretimi

Mermaid ile mimari/sekans diyagramı (README’ye gömülü).

Dokümantasyon ajanı, koddan (docstring/type hints) API referansı üretir ve günceller. 

yago

17) Lisans ve Uyum

Kullanılacak LLM’lerin lisansları (ticari kullanım, model ağırlıkları) kontrol edilir.

Proje lisansı (MIT/Apache-2.0) ve üçüncü parti bağımlılık lisansları gözden geçirilir. 

yago

18) “A’dan Z’ye” Kontrol Listeleri

A – Ajanlar: Roller, araç izinleri, LLM eşleşmesi tanımlandı mı?
B – Bağlam: Prompt şablonları ve proje bağlamı (RAG ops.) hazır mı?
C – CI/CD (lokal): Test/kalite kapıları tanımlandı mı?
D – Dokümantasyon: README + diyagramlar otomatik üretiliyor mu?
E – Entegrasyonlar: Git/FS/Test/Terminal araçları sandbox’ta mı?
F – Failover: Hatalarda yeniden deneme/manuel onay akışı var mı?
G – Güvenlik: Komut kara listesi, workspace izolasyonu aktif mi?
H – Hedefler: MVP başarı kriterleri ölçülüyor mu?
…
Z – Zaman Planı: Faz/takvim ve teslim ölçütleri net mi?
Bu kontrol listesi, faz planınız ve pratik kurulum yönergelerinize dayanır. 

yago

 

yagoO

19) Örnek “Hello World” Senaryosu (Uçtan Uca)

CLI ile fikir girilir → 2) Planlama Ajanı epik/story çıkarır (workspace/PLAN.md).

Dokümantasyon Ajanı README.md taslağını yazar.

Kodlama Ajanı Flask iskeletini ve basit testleri üretir (workspace/app/, tests/).

Test Ajanı pytest’i koşturur; başarısızsa döngü açılır.

Kod İnceleme Ajanı stil ve güvenlik notları verir; Git’e işlenir. 

yagoO

20) Sık Karşılaşılan Sorular

Bulut model gerekli mi? Hayır, hedef tamamen lokal çalışmaktır. 

yago

Model seçimi sabit mi? Hayır, görev bazlı farklı modeller denenebilir. 

yagoO

UI şart mı? MVP için CLI yeterlidir; ileride minimal Web UI eklenebilir. 

yago

Kısa Sonuç

Bu belge, YAGO’nun tam teknik çerçevesini; mimariden kurulum ve örnek koda, test/güvenlikten yol haritasına kadar A’dan Z’ye ortaya koyar. Kavramsal mimari ve faz planı için temel referansınız, uygulamaya yönelik kurulum/örnek kod için de pratik notlarınız baz alınmıştır. 

yago

 

yagoO

İsterseniz bunu tek bir .md dosyası halinde dışa aktarılmış versiyon olarak da paylaşabilirim (aynı içerik).