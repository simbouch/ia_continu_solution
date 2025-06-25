#!/usr/bin/env python3
"""
Setup and deploy Prefect flows for IA Continu Solution Template
This script ensures flows are visible in the Prefect dashboard
"""

import asyncio
from pathlib import Path
import sys

# Add flows to path
flows_dir = Path(__file__).parent / "flows"
sys.path.insert(0, str(flows_dir))

try:
    from data_generation_flow import data_generation_workflow
    from ml_monitoring_flow import ml_monitoring_workflow
    from prefect import serve

    print("✅ Successfully imported Prefect flows")
except ImportError as e:
    print(f"❌ Failed to import flows: {e}")
    sys.exit(1)


def run_flows_once():
    """Run flows once to populate the dashboard with data"""
    print("🚀 Running flows once to populate dashboard...")

    try:
        print("\n--- Running ML Monitoring Flow ---")
        ml_result = ml_monitoring_workflow()
        print(f"✅ ML Monitoring completed: {ml_result.get('status', 'unknown')}")

        print("\n--- Running Data Generation Flow ---")
        data_result = data_generation_workflow(samples=100)
        print(
            f"✅ Data Generation completed: {data_result.get('overall_status', 'unknown')}"
        )

        print("\n🎉 Initial flow runs completed!")
        return True

    except Exception as e:
        print(f"❌ Error running flows: {e}")
        return False


async def serve_flows():
    """Serve flows to make them available in Prefect dashboard"""
    print("📡 Starting Prefect flow server...")

    try:
        # Serve the flows with schedules
        await serve(
            ml_monitoring_workflow.to_deployment(
                name="ml-monitoring",
                interval=120,  # Run every 2 minutes
                tags=["monitoring", "ml", "template"],
            ),
            data_generation_workflow.to_deployment(
                name="data-generation",
                interval=300,  # Run every 5 minutes
                tags=["data", "generation", "template"],
            ),
            limit=10,  # Limit concurrent runs
        )

    except Exception as e:
        print(f"❌ Error serving flows: {e}")


def main():
    """Main setup function"""
    print("🔧 Setting up Prefect flows for IA Continu Solution Template")
    print("=" * 60)

    # First run flows once to populate dashboard
    if run_flows_once():
        print("\n📊 Flows executed successfully!")
        print("🌐 Check Prefect dashboard at: http://localhost:4200")
        print("\n💡 To serve flows continuously, run:")
        print("   python services/prefect/setup_flows.py --serve")
    else:
        print("\n❌ Initial flow execution failed")
        return 1

    # Check if we should serve flows
    if len(sys.argv) > 1 and sys.argv[1] == "--serve":
        print("\n🚀 Starting continuous flow serving...")
        try:
            asyncio.run(serve_flows())
        except KeyboardInterrupt:
            print("\n⏹️ Flow serving stopped by user")
        except Exception as e:
            print(f"\n❌ Flow serving error: {e}")
            return 1

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
