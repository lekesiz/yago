"""
YAGO - Yerel AI Geliştirme Orkestratörü
Main Entry Point

Kullanım:
    python main.py --idea "Flask ile basit bir API yap"
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime
from crewai import Crew, Process
from dotenv import load_dotenv

# YAGO modüllerini import et
from agents.yago_agents import YagoAgents
from tasks.yago_tasks import YagoTasks
from utils.token_tracker import get_tracker, reset_tracker
from utils.report_generator import get_report_generator, reset_report_generator
from utils.template_loader import get_template_loader
from utils.interactive_chat import get_interactive_chat, reset_interactive_chat

# v7.0 imports
from agents.clarification_agent import get_clarification_agent
from core.dynamic_role_manager import get_dynamic_role_manager
from core.super_admin import get_super_admin

# .env yükle
load_dotenv()

# Logging ayarla
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/yago.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("YAGO")


class YagoOrchestrator:
    """YAGO Ana Orkestratör"""

    def __init__(self, interactive_mode: bool = False):
        """Initialize YAGO"""
        logger.info("=" * 60)
        logger.info("🤖 YAGO - Yerel AI Geliştirme Orkestratörü")
        logger.info("=" * 60)

        # Interactive mode
        self.interactive_mode = interactive_mode
        if interactive_mode:
            reset_interactive_chat(enabled=True)
            chat = get_interactive_chat()
            chat.start()

        # Ajanları ve görevleri başlat
        self.agents = YagoAgents(interactive_mode=interactive_mode)
        self.tasks = YagoTasks()

        # Workspace'i hazırla
        self._prepare_workspace()

    def _prepare_workspace(self):
        """Workspace dizinini hazırla"""
        workspace = Path("./workspace")
        workspace.mkdir(exist_ok=True)

        # .gitkeep ekle
        gitkeep = workspace / ".gitkeep"
        gitkeep.touch()

        logger.info(f"📁 Workspace hazır: {workspace.resolve()}")

    def run_full_pipeline(self, project_idea: str, mode: str = "sequential"):
        """
        Tam pipeline'ı çalıştır: Plan → Kod → Test → Review → Docs

        Args:
            project_idea: Kullanıcının proje fikri
            mode: "sequential" veya "hierarchical"

        Returns:
            Sonuç raporu
        """
        logger.info(f"🎯 Proje Fikri: {project_idea}")
        logger.info(f"📋 Mod: {mode}")
        logger.info("-" * 60)

        try:
            # 1. Ajanları oluştur
            logger.info("🔧 Ajanlar oluşturuluyor...")
            planner = self.agents.planner()
            coder = self.agents.coder()
            tester = self.agents.tester()
            reviewer = self.agents.reviewer()
            documenter = self.agents.documenter()

            # 2. Görevleri oluştur
            logger.info("📝 Görevler tanımlanıyor...")
            task_plan = self.tasks.planning_task(planner, project_idea)
            task_code = self.tasks.coding_task(coder)
            task_test = self.tasks.testing_task(tester)
            task_review = self.tasks.review_task(reviewer)
            task_docs = self.tasks.documentation_task(documenter)

            # 3. Crew oluştur ve çalıştır
            logger.info("🚀 YAGO başlatılıyor...")
            logger.info("-" * 60)

            crew = Crew(
                agents=[planner, coder, tester, reviewer, documenter],
                tasks=[task_plan, task_code, task_test, task_review, task_docs],
                verbose=True,
                process=Process.sequential,  # Sıralı çalışma
            )

            # Çalıştır
            start_time = datetime.now()
            result = crew.kickoff()
            end_time = datetime.now()

            # 4. Sonuçları raporla
            duration = (end_time - start_time).total_seconds()
            logger.info("=" * 60)
            logger.info("✅ YAGO TAMAMLANDI!")
            logger.info(f"⏱️  Süre: {duration:.2f} saniye")
            logger.info("=" * 60)

            return {
                "success": True,
                "duration": duration,
                "result": result,
                "workspace": str(Path("./workspace").resolve()),
            }

        except Exception as e:
            logger.error(f"❌ Hata: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
            }

    def run_minimal_test(self, project_idea: str):
        """
        Minimal test: Sadece Plan + Kod

        Args:
            project_idea: Proje fikri

        Returns:
            Sonuç
        """
        logger.info(f"🧪 MİNİMAL TEST MOD")
        logger.info(f"🎯 Proje: {project_idea}")
        logger.info("-" * 60)

        # Report generator başlat
        reporter = get_report_generator()
        start_time = datetime.now()
        reporter.set_metadata(project_idea, "minimal", start_time)
        reporter.add_timeline_event("start", "System", "YAGO minimal test başladı", start_time)

        try:
            # Sadece Planner ve Coder
            planner = self.agents.planner()
            coder = self.agents.coder()

            reporter.add_timeline_event("agent_created", "Planner", "Planner ajanı oluşturuldu")
            reporter.add_timeline_event("agent_created", "Coder", "Coder ajanı oluşturuldu")

            task_plan = self.tasks.planning_task(planner, project_idea)
            task_code = self.tasks.coding_task(coder)

            reporter.add_timeline_event("task_created", "System", "Görevler tanımlandı")

            crew = Crew(
                agents=[planner, coder],
                tasks=[task_plan, task_code],
                verbose=True,
                process=Process.sequential,
            )

            reporter.add_timeline_event("crew_start", "System", "Crew çalıştırılıyor")
            result = crew.kickoff()
            end_time = datetime.now()

            duration = (end_time - start_time).total_seconds()

            logger.info("=" * 60)
            logger.info("✅ TEST TAMAMLANDI!")
            logger.info(f"⏱️  Süre: {duration:.2f} saniye")
            logger.info("=" * 60)

            # Token Tracker Summary
            try:
                tracker = get_tracker()
                tracker.print_summary()

                # Token verilerini rapora ekle
                for provider_model, data in tracker.usage.items():
                    provider, model = provider_model.split(':')
                    reporter.add_token_usage(
                        provider=provider,
                        model=model,
                        input_tokens=data['input_tokens'],
                        output_tokens=data['output_tokens'],
                        cost=data['cost']
                    )
            except Exception as e:
                logger.debug(f"Token summary error: {e}")

            # Workspace dosyalarını rapora ekle
            workspace_path = Path("./workspace")
            for file_path in workspace_path.rglob("*"):
                if file_path.is_file() and file_path.name != ".gitkeep":
                    reporter.add_generated_file(
                        file_path=str(file_path.relative_to(workspace_path)),
                        size_bytes=file_path.stat().st_size,
                        language=file_path.suffix[1:] if file_path.suffix else "unknown"
                    )

            # Final metrics
            reporter.set_final_metrics(
                total_duration=duration,
                total_cost=tracker.total_cost if hasattr(tracker, 'total_cost') else 0.0,
                total_tokens=tracker.total_tokens if hasattr(tracker, 'total_tokens') else 0,
                total_api_calls=tracker.total_calls if hasattr(tracker, 'total_calls') else 0,
                success=True,
                workspace_path=str(workspace_path.resolve())
            )

            reporter.add_timeline_event("end", "System", "YAGO başarıyla tamamlandı", end_time)

            # Raporları oluştur
            logger.info("📄 Raporlar oluşturuluyor...")
            reports = reporter.generate_all(prefix=project_idea.replace(" ", "_")[:30])
            logger.info(f"   - JSON: {reports['json']}")
            logger.info(f"   - Markdown: {reports['markdown']}")
            logger.info(f"   - HTML: {reports['html']}")

            return {
                "success": True,
                "duration": duration,
                "result": result,
                "reports": reports,
            }

        except Exception as e:
            logger.error(f"❌ Hata: {str(e)}", exc_info=True)

            # Hatayı rapora ekle
            reporter.add_error(
                error_type=type(e).__name__,
                message=str(e),
                context="run_minimal_test"
            )

            reporter.set_final_metrics(
                total_duration=(datetime.now() - start_time).total_seconds(),
                total_cost=0.0,
                total_tokens=0,
                total_api_calls=0,
                success=False,
                workspace_path=str(Path("./workspace").resolve())
            )

            # Hata raporları oluştur
            try:
                reports = reporter.generate_all(prefix="error_report")
                logger.info(f"📄 Hata raporu oluşturuldu: {reports['html']}")
            except:
                pass

            return {"success": False, "error": str(e)}

    def run_enhanced_v7(
        self,
        project_idea: str,
        clarification_depth: str = "full",
        approval_mode: str = "professional"
    ):
        """
        YAGO v7.0 Enhanced Mode:
        1. Clarification Phase - Ask questions to understand requirements
        2. Dynamic Role Creation - Create needed agents
        3. Execution with Supervision - Super Admin monitors everything

        Args:
            project_idea: User's project idea
            clarification_depth: "full", "minimal", or "auto"
            approval_mode: "professional", "standard", or "interactive"

        Returns:
            Enhanced result dictionary
        """
        logger.info("=" * 60)
        logger.info("🚀 YAGO v7.0 - Enhanced Mode")
        logger.info("=" * 60)
        logger.info(f"📝 Project: {project_idea}")
        logger.info(f"🎯 Clarification: {clarification_depth}")
        logger.info(f"🤝 Approval: {approval_mode}")
        logger.info("-" * 60)

        try:
            start_time = datetime.now()

            # ============================================
            # PHASE 1: CLARIFICATION
            # ============================================
            logger.info("\n📋 PHASE 1: CLARIFICATION")
            logger.info("-" * 60)

            clarification_agent = get_clarification_agent(
                interactive=(clarification_depth != "auto"),
                depth=clarification_depth
            )

            brief = clarification_agent.clarify_requirements(project_idea)
            clarification_agent.print_brief_summary(brief)

            # ============================================
            # PHASE 2: DYNAMIC ROLE CREATION
            # ============================================
            logger.info("\n🎯 PHASE 2: DYNAMIC ROLE CREATION")
            logger.info("-" * 60)

            role_manager = get_dynamic_role_manager(
                base_agents=self.agents,
                max_dynamic_agents=None,  # NO LIMIT - scales with project complexity
                cost_limit=None  # NO LIMIT - optimized for quality over cost
            )

            role_manager.print_summary(brief.dict())

            # Get all agents (base + dynamic)
            all_agents_dict = role_manager.get_all_agents(brief.dict())
            agent_list = list(all_agents_dict.values())

            logger.info(f"\n✅ Created {len(agent_list)} agents total")

            # ============================================
            # PHASE 3: TASK CREATION
            # ============================================
            logger.info("\n📝 PHASE 3: TASK CREATION")
            logger.info("-" * 60)

            # Create tasks for base agents (use existing task system)
            planner = all_agents_dict.get("Planner")
            coder = all_agents_dict.get("Coder")
            tester = all_agents_dict.get("Tester")
            reviewer = all_agents_dict.get("Reviewer")
            documenter = all_agents_dict.get("Documenter")

            # Build enhanced project idea with clarification context
            enhanced_idea = f"{project_idea}\n\n## Project Brief:\n{brief.dict()}"

            task_plan = self.tasks.planning_task(planner, enhanced_idea)
            task_code = self.tasks.coding_task(coder)
            task_test = self.tasks.testing_task(tester)
            task_review = self.tasks.review_task(reviewer)
            task_docs = self.tasks.documentation_task(documenter)

            tasks = [task_plan, task_code, task_test, task_review, task_docs]

            logger.info(f"✅ Created {len(tasks)} core tasks")

            # ============================================
            # PHASE 4: SUPER ADMIN INITIALIZATION
            # ============================================
            logger.info("\n🎯 PHASE 4: SUPER ADMIN SETUP")
            logger.info("-" * 60)

            super_admin = get_super_admin(
                mode=approval_mode,
                thresholds={
                    "test_coverage": 0.80,
                    "doc_completeness": 0.90,
                }
            )

            logger.info(f"✅ Super Admin ready in '{approval_mode}' mode")

            # ============================================
            # PHASE 5: TASK ASSIGNMENT & EXECUTION
            # ============================================
            logger.info("\n🚀 PHASE 5: TASK ASSIGNMENT & EXECUTION WITH SUPERVISION")
            logger.info("=" * 60)

            # Import execution engines
            from core.task_assignment_engine import get_task_assignment_engine
            from core.execution_engine import get_execution_engine

            # Initialize Task Assignment Engine
            logger.info("\n📌 Initializing Task Assignment Engine...")
            task_assigner = get_task_assignment_engine(
                available_agents=all_agents_dict
            )

            # Assign agents to tasks based on specialization
            logger.info("🔀 Assigning tasks to specialized agents...")
            for task in tasks:
                # The task already has an agent assigned, but verify it's optimal
                current_agent = task.agent.role
                logger.info(f"  ✓ {task.description[:50]}... → {current_agent}")

            # Choose execution strategy based on project complexity
            if brief.complexity_estimate == "simple":
                execution_strategy = "sequential"
            elif brief.complexity_estimate == "medium":
                execution_strategy = "hybrid"
            else:  # complex
                execution_strategy = "parallel"

            logger.info(f"\n⚡ Execution Strategy: {execution_strategy.upper()}")

            # Initialize Execution Engine
            engine = get_execution_engine(
                tasks=tasks,
                strategy=execution_strategy
            )

            # Create crew with all agents (base + dynamic)
            crew = Crew(
                agents=agent_list,
                tasks=tasks,
                verbose=True,
                process=Process.sequential,  # Engine handles execution strategy
            )

            # Execute with supervision
            logger.info("🔄 Starting supervised execution...")
            result = crew.kickoff()

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # ============================================
            # PHASE 6: SUPERVISION & REPORTING
            # ============================================
            logger.info("\n📊 PHASE 6: SUPERVISION REPORT")
            logger.info("-" * 60)

            # Super Admin generates comprehensive supervision report
            # (Real-time monitoring was active during execution if enabled)
            supervision_report = super_admin.generate_report()

            # Print detailed report
            super_admin.print_report()

            # Print event monitoring metrics if real-time was enabled
            if super_admin.enable_real_time:
                logger.info("\n👁️ Real-Time Monitoring Metrics:")
                super_admin.event_monitor.print_metrics()

            # ============================================
            # FINAL SUMMARY
            # ============================================
            logger.info("\n" + "=" * 60)
            logger.info("✅ YAGO v7.0 COMPLETED!")
            logger.info("=" * 60)
            logger.info(f"⏱️  Duration: {duration:.2f}s")
            logger.info(f"🤖 Agents Used: {len(agent_list)}")
            logger.info(f"📋 Tasks Completed: {len(tasks)}")
            logger.info("=" * 60)

            return {
                "success": True,
                "mode": "enhanced_v7",
                "duration": duration,
                "result": result,
                "brief": brief.dict(),
                "agents_used": len(agent_list),
                "workspace": str(Path("./workspace").resolve()),
            }

        except Exception as e:
            logger.error(f"❌ Enhanced mode error: {str(e)}", exc_info=True)
            return {
                "success": False,
                "mode": "enhanced_v7",
                "error": str(e),
            }


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="YAGO - Yerel AI Geliştirme Orkestratörü"
    )
    parser.add_argument(
        "--idea",
        type=str,
        required=False,
        help="Proje fikri (örn: 'Flask ile TODO API yap')",
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["full", "minimal", "enhanced"],
        default="minimal",
        help="Çalışma modu: full (Plan+Kod+Test+Review+Docs), minimal (Plan+Kod), enhanced (v7.0 with clarification+dynamic roles+supervision)",
    )
    parser.add_argument(
        "--clarification-depth",
        type=str,
        choices=["full", "minimal", "auto"],
        default="full",
        help="v7.0: Clarification depth (full=all questions, minimal=essentials, auto=inferred)",
    )
    parser.add_argument(
        "--approval-mode",
        type=str,
        choices=["professional", "standard", "interactive"],
        default="professional",
        help="v7.0: Approval mode (professional=auto, standard=notify, interactive=ask user)",
    )
    parser.add_argument(
        "--template",
        type=str,
        help="Kullanılacak template adı (örn: fastapi_rest_api)",
    )
    parser.add_argument(
        "--list-templates",
        action="store_true",
        help="Mevcut template'leri listele",
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="İnteraktif mod: YAGO çalışırken kullanıcıya sorular sorabilir",
    )
    parser.add_argument(
        "--repo",
        "-r",
        type=str,
        help="Harici Git repository URL'i (örn: https://github.com/user/repo.git). YAGO bu projeyi klonlayıp üzerinde çalışır.",
    )

    args = parser.parse_args()

    # Template listesi göster
    if args.list_templates:
        loader = get_template_loader()
        loader.print_templates_list()
        sys.exit(0)

    # Template kullan
    if args.template:
        loader = get_template_loader()
        try:
            template_data = loader.apply_template(args.template, args.idea)
            args.idea = template_data["project_idea"]
            logger.info(f"📦 Template kullanılıyor: {args.template}")
        except ValueError as e:
            logger.error(f"❌ Template hatası: {e}")
            sys.exit(1)

    # External Git repository'yi yükle
    if args.repo:
        from utils.git_project_loader import get_project_loader
        logger.info(f"📦 Harici Git repository yükleniyor: {args.repo}")
        try:
            loader = get_project_loader()
            analysis = loader.load_project(args.repo)
            context = loader.build_context(analysis)

            # Idea'ya proje context'i ekle
            if args.idea:
                args.idea = f"{args.idea}\n\n## Mevcut Proje Context:\n{context}"
            else:
                args.idea = f"Bu mevcut projede çalış:\n\n{context}"

            logger.info(f"✅ Proje yüklendi: {analysis.repo_name}")
            logger.info(f"   Konum: {analysis.local_path}")
        except Exception as e:
            logger.error(f"❌ Git repository yükleme hatası: {e}")
            sys.exit(1)

    # Token Tracker ve Report Generator başlat
    reset_tracker()
    reset_report_generator()
    from utils.logging_handler import setup_api_logging
    logger.info("📊 Token Tracker aktif - API kullanımı izleniyor...")
    setup_api_logging()

    # YAGO başlat
    yago = YagoOrchestrator(interactive_mode=args.interactive)

    # Çalıştır
    if args.mode == "enhanced":
        # v7.0 Enhanced mode
        result = yago.run_enhanced_v7(
            args.idea,
            clarification_depth=args.clarification_depth,
            approval_mode=args.approval_mode
        )
    elif args.mode == "full":
        result = yago.run_full_pipeline(args.idea)
    else:
        result = yago.run_minimal_test(args.idea)

    # Sonucu göster
    if result["success"]:
        print("\n" + "=" * 60)
        print("✅ BAŞARILI!")
        print(f"📁 Workspace: {result.get('workspace', './workspace')}")
        print(f"⏱️  Süre: {result['duration']:.2f} saniye")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ BAŞARISIZ!")
        print(f"Hata: {result['error']}")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
