"""
Gradio frontend for IT Ops Agent
"""
import gradio as gr
from typing import Optional, Tuple, List
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from datetime import datetime
from src.agents.agent_factory import AgentFactory
from src.agents.base_agent import BaseAgent
from src.config.settings import get_settings


class GradioApp:
    """Gradio application for IT Ops Agent"""
    
    def __init__(self, agent: Optional[BaseAgent] = None):
        """
        Initialize Gradio app
        
        Args:
            agent: Optional agent instance (creates new one using AgentFactory if not provided)
        """
        self.agent = agent or AgentFactory.create_agent()
        self.chat_history: List[Tuple[str, str]] = []
        self.settings = get_settings()
        self.start_time = datetime.utcnow().isoformat()
        self.query_count = 0
        self.error_count = 0
    
    def chat_interface(self, message: str, history: List[Tuple[str, str]]) -> Tuple[str, List[Tuple[str, str]]]:
        """
        Handle chat interface interaction
        
        Args:
            message: User's message
            history: Chat history as list of (user, assistant) tuples
            
        Returns:
            Tuple of (empty string for input, updated history)
        """
        if not message or not message.strip():
            return "", history
        
        # Convert Gradio history format to agent format
        agent_history = []
        for user_msg, assistant_msg in history:
            agent_history.append({"role": "user", "content": user_msg})
            agent_history.append({"role": "assistant", "content": assistant_msg})
        
        # Process query with agent
        try:
            result = self.agent.process_query(message, chat_history=agent_history)
            
            # Get response
            response = result.get("response", "I'm sorry, I couldn't process your request.")
            
            # Add status indicator
            if result.get("success"):
                status = "✅"
            else:
                status = "❌"
            
            # Format response with status
            formatted_response = f"{status} {response}"
            
            # Update history
            history.append((message, formatted_response))
            
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            history.append((message, error_msg))
        
        return "", history
    
    def create_interface(self) -> gr.Blocks:
        """Create and return Gradio interface"""
        
        with gr.Blocks(
            title="IT Ops Agent",
            theme=gr.themes.Soft()
        ) as interface:
            gr.Markdown(
                """
                # IT Ops Agent System
                
                Ask me to help with IT operations tasks like:
                - Password resets (AWS IAM, Active Directory, local accounts)
                - VPN troubleshooting
                - Outlook sync issues
                - Account access requests
                - System diagnostics
                - And more!
                
                I'll retrieve the relevant procedures and execute the necessary commands.
                """
            )
            
            chatbot = gr.Chatbot(
                label="Conversation",
                height=500,
                show_copy_button=True
            )
            
            with gr.Row():
                msg = gr.Textbox(
                    label="Your Message",
                    placeholder="e.g., Reset password for user john.doe",
                    scale=4
                )
                submit_btn = gr.Button("Send", variant="primary", scale=1)
            
            with gr.Row():
                clear_btn = gr.Button("Clear Chat", variant="secondary")
                dry_run_toggle = gr.Checkbox(
                    label="Dry Run Mode",
                    value=False,
                    info="Enable to see what would be executed without actually running commands"
                )
            
            # Event handlers
            def handle_submit(message, history, dry_run):
                if not message or not message.strip():
                    return "", history
                
                # Convert history format
                agent_history = []
                for user_msg, assistant_msg in history:
                    agent_history.append({"role": "user", "content": user_msg})
                    agent_history.append({"role": "assistant", "content": assistant_msg})
                
                # Process with agent
                try:
                    self.query_count += 1
                    result = self.agent.process_query(message, chat_history=agent_history, dry_run=dry_run)
                    response = result.get("response", "I'm sorry, I couldn't process your request.")
                    
                    if result.get("success"):
                        status = "✅"
                    else:
                        self.error_count += 1
                        status = "❌"
                    
                    formatted_response = f"{status} {response}"
                    history.append((message, formatted_response))
                    
                except Exception as e:
                    self.error_count += 1
                    error_msg = f"❌ Error: {str(e)}"
                    history.append((message, error_msg))
                
                return "", history
            
            submit_btn.click(
                fn=handle_submit,
                inputs=[msg, chatbot, dry_run_toggle],
                outputs=[msg, chatbot]
            )
            
            msg.submit(
                fn=handle_submit,
                inputs=[msg, chatbot, dry_run_toggle],
                outputs=[msg, chatbot]
            )
            
            clear_btn.click(
                fn=lambda: ([], ""),
                outputs=[chatbot, msg]
            )
            
            gr.Markdown(
                """
                ### Tips:
                - Be specific about what you want to do (e.g., "Reset password for user john.doe in AWS IAM")
                - Enable Dry Run Mode to see what commands would be executed without actually running them
                - The agent will retrieve relevant procedures and execute commands automatically
                """
            )
        
        return interface
    
    def add_health_check(self, app: FastAPI):
        """Add health check endpoint to FastAPI app"""
        @app.get("/health")
        async def health_check():
            """Health check endpoint for container orchestration"""
            try:
                # Basic health check - verify agent is initialized
                if self.agent is None:
                    return JSONResponse(
                        status_code=503,
                        content={"status": "unhealthy", "reason": "Agent not initialized"}
                    )
                return JSONResponse(
                    status_code=200,
                    content={"status": "healthy", "service": "itops-agent"}
                )
            except Exception as e:
                return JSONResponse(
                    status_code=503,
                    content={"status": "unhealthy", "reason": str(e)}
                )
    
    def add_metrics_endpoint(self, app: FastAPI):
        """Add metrics endpoint for monitoring (Prometheus-compatible format)"""
        @app.get("/metrics")
        async def metrics():
            """
            Metrics endpoint for monitoring and observability
            Returns metrics in Prometheus-compatible format
            """
            try:
                # Calculate uptime
                uptime_seconds = (datetime.utcnow() - datetime.fromisoformat(self.start_time)).total_seconds()
                
                # Basic metrics in Prometheus format
                metrics_text = f"""# HELP itops_agent_queries_total Total number of queries processed
# TYPE itops_agent_queries_total counter
itops_agent_queries_total {self.query_count}

# HELP itops_agent_errors_total Total number of errors
# TYPE itops_agent_errors_total counter
itops_agent_errors_total {self.error_count}

# HELP itops_agent_uptime_seconds Uptime in seconds
# TYPE itops_agent_uptime_seconds gauge
itops_agent_uptime_seconds {uptime_seconds}

# HELP itops_agent_healthy Service health status (1=healthy, 0=unhealthy)
# TYPE itops_agent_healthy gauge
itops_agent_healthy {1 if self.agent is not None else 0}
"""
                
                # Calculate success rate if we have queries
                if self.query_count > 0:
                    success_rate = (self.query_count - self.error_count) / self.query_count
                    metrics_text += f"""
# HELP itops_agent_success_rate Success rate (0-1)
# TYPE itops_agent_success_rate gauge
itops_agent_success_rate {success_rate}
"""
                
                from fastapi.responses import Response
                return Response(content=metrics_text, media_type="text/plain")
                
            except Exception as e:
                return JSONResponse(
                    status_code=500,
                    content={"error": "Failed to generate metrics", "reason": str(e)}
                )
        
        @app.get("/metrics/json")
        async def metrics_json():
            """
            Metrics endpoint in JSON format for easier consumption
            """
            try:
                uptime_seconds = (datetime.utcnow() - datetime.fromisoformat(self.start_time)).total_seconds()
                
                metrics_data = {
                    "service": "itops-agent",
                    "start_time": self.start_time,
                    "uptime_seconds": uptime_seconds,
                    "queries_total": self.query_count,
                    "errors_total": self.error_count,
                    "healthy": self.agent is not None
                }
                
                if self.query_count > 0:
                    metrics_data["success_rate"] = (self.query_count - self.error_count) / self.query_count
                else:
                    metrics_data["success_rate"] = None
                
                return JSONResponse(content=metrics_data)
                
            except Exception as e:
                return JSONResponse(
                    status_code=500,
                    content={"error": "Failed to generate metrics", "reason": str(e)}
                )
    
    def launch(self, share: bool = False, server_name: Optional[str] = None, server_port: Optional[int] = None):
        """
        Launch the Gradio interface
        
        Args:
            share: Whether to create a public link
            server_name: Server hostname (defaults to config)
            server_port: Server port (defaults to config)
        """
        interface = self.create_interface()
        
        # Add health check and metrics endpoints before launching
        # Gradio Blocks exposes FastAPI app via .app attribute
        try:
            app = interface.app
            self.add_health_check(app)
            self.add_metrics_endpoint(app)
        except AttributeError:
            # If app is not available yet, add it after launch
            # This is a fallback for different Gradio versions
            pass
        
        interface.launch(
            server_name=server_name or self.settings.app_host,
            server_port=server_port or self.settings.app_port,
            share=share
        )
        
        # Try to add health check and metrics after launch if not added before
        try:
            if hasattr(interface, 'app') and interface.app:
                self.add_health_check(interface.app)
                self.add_metrics_endpoint(interface.app)
        except Exception:
            # Endpoints are optional, don't fail if they can't be added
            pass


def main():
    """Main entry point for Gradio app"""
    app = GradioApp()
    app.launch()


if __name__ == "__main__":
    main()

