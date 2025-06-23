#!/usr/bin/env python3
"""
Deploy and run Prefect flows for IA Continu Solution
This script deploys flows and runs them to populate the dashboard
"""

import asyncio
import sys
import time
from pathlib import Path

# Add flows to path
flows_dir = Path(__file__).parent / "flows"
sys.path.insert(0, str(flows_dir))

try:
    from prefect import serve
    from prefect.client.orchestration import PrefectClient
    from ml_monitoring_flow import ml_monitoring_workflow
    from data_generation_flow import data_generation_workflow
    print("✅ Successfully imported Prefect flows")
except ImportError as e:
    print(f"❌ Failed to import flows: {e}")
    sys.exit(1)


async def deploy_flows():
    """Deploy flows to Prefect server"""
    print("📡 Deploying flows to Prefect server...")
    
    try:
        # Create deployments
        ml_deployment = ml_monitoring_workflow.to_deployment(
            name="ml-monitoring-deployment",
            interval=120,  # Run every 2 minutes
            tags=["monitoring", "ml", "automated"],
            description="Automated ML monitoring with drift detection"
        )
        
        data_deployment = data_generation_workflow.to_deployment(
            name="data-generation-deployment", 
            interval=300,  # Run every 5 minutes
            tags=["data", "generation", "automated"],
            description="Automated data generation for ML pipeline"
        )
        
        # Deploy to server
        await ml_deployment.apply()
        await data_deployment.apply()
        
        print("✅ Flows deployed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error deploying flows: {e}")
        return False


def run_flows_once():
    """Run flows once to populate the dashboard"""
    print("🚀 Running flows once to populate dashboard...")
    
    try:
        print("\n--- Running ML Monitoring Flow ---")
        ml_result = ml_monitoring_workflow()
        print(f"✅ ML Monitoring completed: {ml_result.get('status', 'unknown')}")
        
        print("\n--- Running Data Generation Flow ---")
        data_result = data_generation_workflow(samples=100)
        print(f"✅ Data Generation completed: {data_result.get('overall_status', 'unknown')}")
        
        print("\n🎉 Initial flow runs completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error running flows: {e}")
        import traceback
        traceback.print_exc()
        return False


async def serve_flows():
    """Serve flows continuously"""
    print("🔄 Starting continuous flow serving...")
    
    try:
        await serve(
            ml_monitoring_workflow.to_deployment(
                name="ml-monitoring-serve",
                interval=120,  # Run every 2 minutes
                tags=["monitoring", "ml", "continuous"]
            ),
            data_generation_workflow.to_deployment(
                name="data-generation-serve", 
                interval=300,  # Run every 5 minutes
                tags=["data", "generation", "continuous"]
            ),
            limit=10  # Limit concurrent runs
        )
        
    except Exception as e:
        print(f"❌ Error serving flows: {e}")


async def check_prefect_connection():
    """Check connection to Prefect server"""
    try:
        async with PrefectClient() as client:
            server_info = await client.hello()
            print(f"✅ Connected to Prefect server: {server_info}")
            return True
    except Exception as e:
        print(f"❌ Cannot connect to Prefect server: {e}")
        return False


async def main():
    """Main function"""
    print("🔧 Setting up Prefect flows for IA Continu Solution")
    print("=" * 60)
    
    # Check connection first
    if not await check_prefect_connection():
        print("❌ Cannot connect to Prefect server. Make sure it's running.")
        return 1
    
    # Deploy flows
    if not await deploy_flows():
        print("❌ Failed to deploy flows")
        return 1
    
    # Run flows once to populate dashboard
    if run_flows_once():
        print("\n📊 Flows executed successfully!")
        print("🌐 Check Prefect dashboard at: http://localhost:4200")
    else:
        print("\n❌ Initial flow execution failed")
        return 1
    
    # Check if we should serve flows continuously
    if len(sys.argv) > 1 and sys.argv[1] == "--serve":
        print("\n🚀 Starting continuous flow serving...")
        try:
            await serve_flows()
        except KeyboardInterrupt:
            print("\n⏹️ Flow serving stopped by user")
        except Exception as e:
            print(f"\n❌ Flow serving error: {e}")
            return 1
    else:
        print("\n💡 To serve flows continuously, run:")
        print("   python services/prefect/deploy_and_run.py --serve")
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
