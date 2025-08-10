#!/usr/bin/env python3
"""
Execute data pipeline test on AWS EC2 instance
"""

import subprocess
import sys
import os
from datetime import datetime

def run_aws_test():
    """Run the data pipeline test on AWS"""
    print("R26 AWS Data Pipeline Test Executor")
    print("=" * 60)
    print(f"Started at: {datetime.now()}")
    
    # AWS connection details
    aws_ip = "54.198.134.93"
    key_path = "keys/research-26-key.pem"
    
    # Check if key file exists
    if not os.path.exists(key_path):
        print(f"❌ SSH key not found at: {key_path}")
        print("Please ensure the SSH key is in the correct location")
        return False
    
    print(f"✅ SSH key found: {key_path}")
    print(f"✅ Target AWS instance: {aws_ip}")
    
    # Commands to run on AWS
    commands = [
        # Navigate to project directory
        "cd /home/ec2-user/research-26-trading-system",
        
        # Pull latest code from GitHub
        "git pull origin main",
        
        # Run the data pipeline test
        "python3 test_aws_data_pipeline.py",
        
        # Copy test results to a location we can access
        "cp /tmp/r26_data_pipeline_test_report.json /home/ec2-user/",
        
        # Show the test report
        "cat /home/ec2-user/r26_data_pipeline_test_report.json"
    ]
    
    # Combine commands with &&
    full_command = " && ".join(commands)
    
    # SSH command
    ssh_command = [
        "ssh",
        "-i", key_path,
        "-o", "StrictHostKeyChecking=no",
        f"ec2-user@{aws_ip}",
        full_command
    ]
    
    print(f"✅ Executing SSH command...")
    print(f"Command: {' '.join(ssh_command[:4])} [REDACTED] {full_command}")
    
    try:
        # Execute the command
        result = subprocess.run(
            ssh_command,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        print("\n" + "=" * 60)
        print("AWS TEST OUTPUT")
        print("=" * 60)
        print(result.stdout)
        
        if result.stderr:
            print("\n" + "=" * 60)
            print("ERROR OUTPUT")
            print("=" * 60)
            print(result.stderr)
        
        if result.returncode == 0:
            print("\n✅ AWS data pipeline test completed successfully!")
            return True
        else:
            print(f"\n❌ AWS test failed with return code: {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Test timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"❌ Failed to execute test: {e}")
        return False

def main():
    """Main execution"""
    success = run_aws_test()
    
    if success:
        print("\n🎉 R26 Data Pipeline Test: SUCCESS")
        print("Next step: Analyze results and proceed with Phase 2")
    else:
        print("\n💥 R26 Data Pipeline Test: FAILED")
        print("Check the error output above and resolve issues")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
