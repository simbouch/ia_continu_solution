"""
Deploy Prefect flows for IA Continu Solution
"""

import asyncio
from datetime import timedelta
from pathlib import Path
import sys

from prefect.deployments import Deployment
from prefect.server.schemas.schedules import IntervalSchedule

# Add the flows directory to the path
flows_dir = Path(__file__).parent / "flows"
sys.path.insert(0, str(flows_dir))

# Import the flows - must be after path modification
try:
    from data_generation_flow import data_generation_workflow
    from ml_monitoring_flow import ml_monitoring_workflow
except ImportError as e:
    print(f"Warning: Could not import flows: {e}")
    data_generation_workflow = None
    ml_monitoring_workflow = None


async def deploy_flows():
    """Deploy all flows to Prefect server"""
    print("🚀 Deploying Prefect flows...")

    # Create deployments
    ml_monitoring_deployment = Deployment.build_from_flow(
        flow=ml_monitoring_workflow,
        name="ml-monitoring-deployment",
        description="Automated ML monitoring and drift detection",
        schedule=IntervalSchedule(interval=timedelta(minutes=2)),  # Run every 2 minutes
        work_pool_name="default-agent-pool",
        tags=["monitoring", "ml", "automated"],
    )

    data_generation_deployment = Deployment.build_from_flow(
        flow=data_generation_workflow,
        name="data-generation-deployment",
        description="Automated data generation and validation",
        schedule=IntervalSchedule(interval=timedelta(minutes=5)),  # Run every 5 minutes
        work_pool_name="default-agent-pool",
        tags=["data", "generation", "automated"],
    )

    # Deploy the flows
    ml_monitoring_id = await ml_monitoring_deployment.apply()
    data_generation_id = await data_generation_deployment.apply()

    print(f"✅ ML Monitoring deployment created: {ml_monitoring_id}")
    print(f"✅ Data Generation deployment created: {data_generation_id}")

    return ml_monitoring_id, data_generation_id


def run_flows_manually():
    """Run flows manually for immediate testing"""
    print("🔄 Running flows manually for testing...")

    try:
        print("\n--- Running ML Monitoring Flow ---")
        ml_result = ml_monitoring_workflow()
        print(f"ML Monitoring Result: {ml_result['status']}")

        print("\n--- Running Data Generation Flow ---")
        data_result = data_generation_workflow(samples=200)
        print(f"Data Generation Result: {data_result['overall_status']}")

        print("\n✅ Manual flow execution completed!")

    except Exception as e:
        print(f"❌ Error running flows manually: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Deploy and manage Prefect flows")
    parser.add_argument(
        "--deploy", action="store_true", help="Deploy flows to Prefect server"
    )
    parser.add_argument("--run", action="store_true", help="Run flows manually")
    parser.add_argument("--both", action="store_true", help="Deploy and run flows")

    args = parser.parse_args()

    if args.both or args.run or (not args.deploy and not args.run):
        # Run manually first to test
        run_flows_manually()

    if args.both or args.deploy:
        # Deploy to server
        asyncio.run(deploy_flows())

    print("\n🎉 Prefect flows setup completed!")
    print("📊 Check the Prefect UI at http://localhost:4200 to see your flows and runs")
