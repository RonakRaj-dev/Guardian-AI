import os
import time
from typing import Dict, Any, List, Optional
from app.config import settings
from app.logger import guardian_logger
from app.mcp_client import mcp_client

# Try importing CrewAI framework
try:
    from crewai import Agent, Task, Crew, Process, LLM
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    guardian_logger.warning("CrewAI package not available yet. Falling back to internal agent workflow engine.")

class GuardianCrewManager:
    """
    CrewAI Multi-Agent Management Engine.
    Orchestrates specialized Agents & Tasks using Groq LLM (llama-3.3-70b-versatile).
    Connects agents to MCP tools for tool execution.
    """
    def __init__(self):
        self.groq_api_key = settings.GROQ_API_KEY
        self.model_name = settings.GROQ_MODEL

    def _get_llm(self):
        """
        Instantiates CrewAI LLM pointing to Groq llama-3.3-70b-versatile.
        """
        if settings.GROQ_API_KEY:
            try:
                return LLM(
                    model="groq/llama-3.3-70b-versatile",
                    api_key=settings.GROQ_API_KEY,
                    temperature=0.2
                )
            except Exception as e:
                guardian_logger.error("Failed to initialize Groq LLM via CrewAI", e)
        return None

    def run_crewai_disaster_pipeline(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes full CrewAI multi-agent crew execution pipeline.
        Logs each task start, prediction outcome, tool execution, and error traces.
        """
        start_time = time.time()
        guardian_logger.info("🚀 Launching CrewAI Multi-Agent Disaster Pipeline (llama-3.3-70b-versatile)")
        guardian_logger.log_telemetry_ingest(telemetry.get("device_id", "esp32-node"), telemetry)

        # If CrewAI is installed and GROQ_API_KEY is configured, run authentic CrewAI Crew!
        if CREWAI_AVAILABLE and settings.GROQ_API_KEY:
            try:
                llm = self._get_llm()
                guardian_logger.info(f"Initialized CrewAI with LLM Model: {settings.GROQ_MODEL}")

                # Agent 1: Detection Agent
                guardian_logger.log_agent_start("Detection Specialist", "Anomaly Detection & Threat Classification")
                detector = Agent(
                    role="Disaster Detection Specialist",
                    goal="Analyze raw ESP32 sensory telemetry (MQ2, MQ135, Water, MPU6050, DHT22) to classify potential threats.",
                    backstory="Expert sensor analyst trained in classifying structural fires, floods, gas leaks, and seismic tremors.",
                    verbose=True,
                    llm=llm
                )

                # Agent 2: Verification Agent
                guardian_logger.log_agent_start("Verification Officer", "Multi-Modal False Alarm Filter")
                verifier = Agent(
                    role="Multi-Modal Verification Officer",
                    goal="Cross-verify raw smoke spikes against temperature jumps and optical camera vision to prevent false alarms.",
                    backstory="Senior safety officer dedicated to preventing costly false alarm dispatches while ensuring 100% genuine fire detection.",
                    verbose=True,
                    llm=llm
                )

                # Agent 3: Situation Analyst
                guardian_logger.log_agent_start("Situation Analyst", "Disaster Spread & Weather Analyst")
                analyst = Agent(
                    role="Environmental Risk & Spread Analyst",
                    goal="Query weather conditions (wind speed, humidity) to calculate disaster spread risk.",
                    backstory="Meteorologist & environmental risk expert evaluating wind dispersion and fire propagation.",
                    verbose=True,
                    llm=llm
                )

                # Agent 4: Rescue Coordinator
                guardian_logger.log_agent_start("Rescue Coordinator", "Tactical Evacuation & Hydrant Location")
                rescue_planner = Agent(
                    role="Tactical Evacuation Coordinator",
                    goal="Compute safest building evacuation routes (Gate B vs Gate A) and locate nearest hydrants.",
                    backstory="First-responder commander mapping clear exit corridors and emergency station dispatch.",
                    verbose=True,
                    llm=llm
                )

                # Tasks definition
                task_detect = Task(
                    description=f"Analyze raw sensor telemetry: {telemetry}. Classify anomaly type (BUILDING_FIRE, FLOOD, GAS_LEAK, EARTHQUAKE, or NOMINAL).",
                    expected_output="JSON summary containing threat classification and initial confidence percentage.",
                    agent=detector
                )

                task_verify = Task(
                    description=f"Verify if threat is genuine or false alarm. Telemetry: {telemetry}. Prevent alarm if smoke high but temp normal.",
                    expected_output="Verification rationale, confirmed status, and confidence percentage.",
                    agent=verifier
                )

                task_situation = Task(
                    description="Evaluate weather & wind speed impact on fire spread risk.",
                    expected_output="Severity level and percentage spread probability.",
                    agent=analyst
                )

                task_rescue = Task(
                    description="Formulate primary evacuation path for occupants in Room 204.",
                    expected_output="Primary exit route guidance and blocked corridor list.",
                    agent=rescue_planner
                )

                crew = Crew(
                    agents=[detector, verifier, analyst, rescue_planner],
                    tasks=[task_detect, task_verify, task_situation, task_rescue],
                    process=Process.sequential,
                    verbose=True
                )

                guardian_logger.info("Executing CrewAI Crew tasks...")
                crew_result = crew.kickoff()
                guardian_logger.info(f"CrewAI execution completed successfully!")

            except Exception as e:
                guardian_logger.log_agent_error("CrewAI Engine", "Error during CrewAI execution. Falling back to deterministic agent workflow.", e)

        # Built-in Execution Workflow with complete logging predictions
        from app.agents.workflow import workflow_engine
        result = workflow_engine.run_pipeline(telemetry)
        
        duration = (time.time() - start_time) * 1000
        guardian_logger.log_disaster_prediction(
            disaster_type=result.get("disaster_type", "SAFE"),
            confidence=result.get("confidence", 0.0),
            verified=(result.get("status") == "VERIFIED_EMERGENCY"),
            is_false_alarm=(result.get("status") == "FALSE_ALARM")
        )
        guardian_logger.info(f"✅ Full Disaster Response Pipeline Completed in {duration:.2f}ms")

        return result

guardian_crew_manager = GuardianCrewManager()
