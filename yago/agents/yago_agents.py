"""
YAGO Expert Agents - Uzman AI Ajanları
Her ajan farklı API kullanır (OpenAI, Claude, Gemini)
"""

from crewai import Agent
from .base_agent import BaseAgent
from tools.file_tools import FileTools
from tools.terminal_tools import TerminalTools
from tools.interactive_tools import get_interactive_tools
from tools.debug_tools import get_debug_tools
from tools.git_tools import get_git_tools
from tools.quality_tools import get_quality_tools
from tools.project_tools import get_project_tools


class YagoAgents(BaseAgent):
    """YAGO Uzman Ajanları Yöneticisi"""

    def __init__(self, config_path: str = "yago_config.yaml", interactive_mode: bool = False, auto_debug: bool = True):
        super().__init__(config_path)

        # Tools initialization
        self.file_tools = FileTools()
        self.terminal_tools = TerminalTools()

        # Interactive tools (optional)
        self.interactive_mode = interactive_mode
        self.interactive_tools = get_interactive_tools() if interactive_mode else []

        # Debug tools (enabled by default)
        self.auto_debug = auto_debug
        self.debug_tools = get_debug_tools() if auto_debug else []

        # Project tools (for external Git repos)
        self.project_tools = get_project_tools()

    def planner(self) -> Agent:
        """
        Planlama Ajanı - Claude
        Teknik mimari ve proje planlaması yapar
        Interactive mode: Can ask user for clarification on requirements
        Project tools: Can load and analyze external Git repositories
        """
        tools = []

        # Add project tools (for external Git repos)
        tools.extend(self.project_tools)

        # Add interactive tools if enabled
        if self.interactive_mode:
            tools.extend(self.interactive_tools)

        return self.create_agent(
            agent_type="planner",
            tools=tools,
            allow_delegation=False,
        )

    def coder(self) -> Agent:
        """
        Kodlama Ajanı - OpenAI GPT-4
        Kod yazar, refactor yapar
        Interactive mode: Can ask for technical decisions during coding
        Auto-debug: Automatically checks syntax and fixes common errors
        """
        tools = [
            self.file_tools.write_file,
            self.file_tools.read_file,
            self.file_tools.list_files,
            self.terminal_tools.run_command,
            self.terminal_tools.run_python,
        ]
        # Add debug tools if enabled
        if self.auto_debug:
            tools.extend(self.debug_tools)

        # Add interactive tools if enabled
        if self.interactive_mode:
            tools.extend(self.interactive_tools)

        return self.create_agent(
            agent_type="coder",
            tools=tools,
            allow_delegation=False,
        )

    def tester(self) -> Agent:
        """
        Test Ajanı - Gemini
        Test yazar ve çalıştırır
        Auto-debug: Can run tests with detailed error analysis
        """
        tools = [
            self.file_tools.write_file,
            self.file_tools.read_file,
            self.file_tools.list_files,
            self.terminal_tools.run_tests,
            self.terminal_tools.run_python,
        ]

        # Add debug tools if enabled
        if self.auto_debug:
            tools.extend(self.debug_tools)

        return self.create_agent(
            agent_type="tester",
            tools=tools,
            allow_delegation=False,
        )

    def reviewer(self) -> Agent:
        """
        Kod İnceleme Ajanı - Claude
        Kod kalitesi ve güvenlik kontrolü yapar
        """
        return self.create_agent(
            agent_type="reviewer",
            tools=[
                self.file_tools.read_file,
                self.file_tools.list_files,
            ],
            allow_delegation=False,
        )

    def documenter(self) -> Agent:
        """
        Dokümantasyon Ajanı - OpenAI GPT-4
        README, API docs üretir
        """
        return self.create_agent(
            agent_type="documenter",
            tools=[
                self.file_tools.write_file,
                self.file_tools.read_file,
                self.file_tools.list_files,
            ],
            allow_delegation=False,
        )

    def orchestrator(self) -> Agent:
        """
        Master Orchestrator - Claude
        Tüm ajanları koordine eder
        """
        return self.create_agent(
            agent_type="orchestrator",
            tools=[],  # Orchestrator sadece koordine eder
            allow_delegation=True,  # Görev devri yapabilir
        )
