"""
Weights & Biases Logger for ReactionReach

Custom logging utilities for tracking LinkedIn automation performance,
agent metrics, and intelligence gathering insights.
"""

import weave
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

class ReactionReachLogger:
    """Custom logger for ReactionReach metrics and performance tracking"""
    
    def __init__(self, run_id: Optional[str] = None):
        self.start_time = time.time()
        self.run_id = run_id or f"reaction-reach-{int(time.time())}"
        self.metrics = {}
        self.task_timings = {}
        
        # Initialize run metadata
        weave.log({
            "run_id": self.run_id,
            "run_start_time": datetime.now().isoformat(),
            "logger_initialized": True
        })
    
    @weave.op()
    def log_navigation_attempt(self, profile_url: str, success: bool, error_msg: str = None):
        """Log LinkedIn navigation attempts and success rates"""
        
        navigation_data = {
            "navigation_success": success,
            "profile_url": profile_url,
            "timestamp": datetime.now().isoformat(),
            "run_id": self.run_id
        }
        
        if error_msg:
            navigation_data["error_message"] = error_msg
        
        weave.log(navigation_data)
        
        # Update success rate metrics
        if "navigation_attempts" not in self.metrics:
            self.metrics["navigation_attempts"] = 0
            self.metrics["navigation_successes"] = 0
            
        self.metrics["navigation_attempts"] += 1
        if success:
            self.metrics["navigation_successes"] += 1
            
        success_rate = self.metrics["navigation_successes"] / self.metrics["navigation_attempts"]
        weave.log({"navigation_success_rate": success_rate})
    
    @weave.op()
    def log_post_discovery(self, posts_found: int, target_posts: int, discovery_time: float):
        """Log post discovery performance and efficiency"""
        
        discovery_rate = posts_found / target_posts if target_posts > 0 else 0
        posts_per_second = posts_found / discovery_time if discovery_time > 0 else 0
        
        discovery_data = {
            "posts_discovered": posts_found,
            "target_posts": target_posts,
            "discovery_rate": discovery_rate,
            "discovery_time_seconds": discovery_time,
            "posts_per_second": posts_per_second,
            "run_id": self.run_id,
            "timestamp": datetime.now().isoformat()
        }
        
        weave.log(discovery_data)
        
        # Track cumulative discovery metrics
        self.metrics["total_posts_discovered"] = posts_found
        self.metrics["avg_discovery_rate"] = discovery_rate
    
    @weave.op()
    def log_reaction_extraction(self, post_id: str, reactions_extracted: int, 
                               extraction_time: float, post_url: str = None):
        """Log reaction extraction performance per post"""
        
        reactions_per_second = reactions_extracted / extraction_time if extraction_time > 0 else 0
        
        extraction_data = {
            "post_id": post_id,
            "post_url": post_url,
            "reactions_extracted": reactions_extracted,
            "extraction_time_seconds": extraction_time,
            "reactions_per_second": reactions_per_second,
            "run_id": self.run_id,
            "timestamp": datetime.now().isoformat()
        }
        
        weave.log(extraction_data)
        
        # Update cumulative extraction metrics
        if "total_reactions_extracted" not in self.metrics:
            self.metrics["total_reactions_extracted"] = 0
            self.metrics["total_extraction_time"] = 0
            
        self.metrics["total_reactions_extracted"] += reactions_extracted
        self.metrics["total_extraction_time"] += extraction_time
        
        # Calculate average extraction rate
        avg_rate = (self.metrics["total_reactions_extracted"] / 
                   self.metrics["total_extraction_time"] if self.metrics["total_extraction_time"] > 0 else 0)
        weave.log({"avg_reactions_per_second": avg_rate})
    
    @weave.op()
    def log_analysis_insights(self, insights: Dict[str, Any]):
        """Log analysis results and intelligence quality metrics"""
        
        # Extract key metrics from insights
        top_engagers = insights.get("top_engagers", [])
        total_reactions = insights.get("total_reactions", 0)
        unique_companies = insights.get("unique_companies", [])
        reaction_types = insights.get("reaction_types", {})
        
        analysis_data = {
            "top_engagers_count": len(top_engagers),
            "total_reactions_analyzed": total_reactions,
            "unique_companies_count": len(unique_companies),
            "reaction_types_found": len(reaction_types),
            "analysis_completion_time": time.time() - self.start_time,
            "run_id": self.run_id,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add reaction type distribution
        if reaction_types:
            for reaction_type, count in reaction_types.items():
                analysis_data[f"reaction_type_{reaction_type}"] = count
        
        weave.log(analysis_data)
        
        # Store top engagers for further analysis
        if top_engagers:
            for i, engager in enumerate(top_engagers[:10]):  # Top 10
                weave.log({
                    "top_engager_rank": i + 1,
                    "engager_name": engager.get("name", "Unknown"),
                    "engager_company": engager.get("company", "Unknown"),
                    "engagement_count": engager.get("engagement_count", 0),
                    "run_id": self.run_id
                })
    
    @weave.op()
    def log_task_performance(self, task_name: str, duration: float, success: bool, 
                           agent_name: str = None, output_size: int = None):
        """Log individual task performance metrics"""
        
        task_data = {
            "task_name": task_name,
            "agent_name": agent_name,
            "duration_seconds": duration,
            "success": success,
            "output_size_chars": output_size,
            "run_id": self.run_id,
            "timestamp": datetime.now().isoformat()
        }
        
        weave.log(task_data)
        
        # Track task timings
        self.task_timings[task_name] = duration
    
    @weave.op()
    def log_crew_performance(self, crew_result, total_agents: int = 5):
        """Log overall crew performance and execution metrics"""
        
        total_execution_time = time.time() - self.start_time
        tasks_completed = len(crew_result.tasks_output) if crew_result and hasattr(crew_result, 'tasks_output') else 0
        success = crew_result is not None
        
        crew_data = {
            "total_execution_time_seconds": total_execution_time,
            "total_execution_time_minutes": total_execution_time / 60,
            "crew_success": success,
            "tasks_completed": tasks_completed,
            "total_agents": total_agents,
            "completion_rate": tasks_completed / total_agents if total_agents > 0 else 0,
            "run_id": self.run_id,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add task timing breakdown
        for task_name, duration in self.task_timings.items():
            crew_data[f"task_duration_{task_name}"] = duration
        
        # Add cumulative metrics
        crew_data.update(self.metrics)
        
        weave.log(crew_data)
        
        return crew_data
    
    @weave.op()
    def log_error(self, error_type: str, error_message: str, task_name: str = None, 
                  agent_name: str = None, context: Dict[str, Any] = None):
        """Log errors and exceptions for debugging"""
        
        error_data = {
            "error_type": error_type,
            "error_message": error_message,
            "task_name": task_name,
            "agent_name": agent_name,
            "run_id": self.run_id,
            "timestamp": datetime.now().isoformat(),
            "execution_time_at_error": time.time() - self.start_time
        }
        
        if context:
            error_data["error_context"] = context
        
        weave.log(error_data)
    
    @weave.op()
    def log_rate_limiting(self, action: str, delay_seconds: float, reason: str = None):
        """Log rate limiting actions for compliance tracking"""
        
        rate_limit_data = {
            "rate_limit_action": action,
            "delay_seconds": delay_seconds,
            "reason": reason,
            "run_id": self.run_id,
            "timestamp": datetime.now().isoformat()
        }
        
        weave.log(rate_limit_data)
    
    @weave.op()
    def log_stealth_metrics(self, detection_avoided: bool, session_rotated: bool = False,
                           captcha_encountered: bool = False):
        """Log stealth operation effectiveness"""
        
        stealth_data = {
            "detection_avoided": detection_avoided,
            "session_rotated": session_rotated,
            "captcha_encountered": captcha_encountered,
            "run_id": self.run_id,
            "timestamp": datetime.now().isoformat()
        }
        
        weave.log(stealth_data)
    
    def get_run_summary(self) -> Dict[str, Any]:
        """Get a summary of the current run metrics"""
        
        total_time = time.time() - self.start_time
        
        summary = {
            "run_id": self.run_id,
            "total_execution_time": total_time,
            "metrics": self.metrics.copy(),
            "task_timings": self.task_timings.copy(),
            "timestamp": datetime.now().isoformat()
        }
        
        return summary

# Decorator for automatic function timing
def track_execution_time(logger: ReactionReachLogger, task_name: str):
    """Decorator to automatically track function execution time"""
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            result = None
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                logger.log_error(
                    error_type=type(e).__name__,
                    error_message=str(e),
                    task_name=task_name
                )
                raise
            finally:
                duration = time.time() - start_time
                output_size = len(str(result)) if result else 0
                
                logger.log_task_performance(
                    task_name=task_name,
                    duration=duration,
                    success=success,
                    output_size=output_size
                )
        
        return wrapper
    return decorator

# Example usage patterns
if __name__ == "__main__":
    # Example of how to use the logger
    logger = ReactionReachLogger()
    
    # Log navigation
    logger.log_navigation_attempt("https://linkedin.com/in/example", True)
    
    # Log post discovery
    logger.log_post_discovery(posts_found=15, target_posts=20, discovery_time=45.5)
    
    # Log reaction extraction
    logger.log_reaction_extraction(
        post_id="post_123",
        reactions_extracted=25,
        extraction_time=12.3,
        post_url="https://linkedin.com/feed/update/123"
    )
    
    print("Logger example completed!")