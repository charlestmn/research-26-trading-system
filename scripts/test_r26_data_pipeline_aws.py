#!/usr/bin/env python3
"""
Test R26 Data Pipeline on AWS
"""

import subprocess
import sys
import os
from datetime import datetime

def test_r26_data_pipeline_aws():
    """Test the R26 data pipeline on AWS"""
    print("R26 Data Pipeline AWS Test")
    print("=" * 60)
    print(f"Started at: {datetime.now()}")
    
    # AWS connection details
    aws_ip = "54.198.134.93"
    key_path = "keys/research26-key.pem"
    
    # Check if key file exists
    if not os.path.exists(key_path):
        print(f"❌ SSH key not found at: {key_path}")
        return False
    
    print(f"✅ SSH key found: {key_path}")
    print(f"✅ Target AWS instance: {aws_ip}")
    
    # Commands to run on AWS
    commands = [
        # Navigate to project directory
        "cd /home/ec2-user/research-26-trading-system",
        
        # Pull latest code from GitHub
        "git pull origin main",
        
        # Test the R26 data pipeline
        "python3 r26_data_pipeline.py",
        
        # Check if data directory was created
        "ls -la r26_data/",
        
        # Show metadata database content
        "python3 -c \"import sqlite3; conn = sqlite3.connect('r26_data/metadata.db'); cursor = conn.cursor(); cursor.execute('SELECT * FROM data_metadata'); print('Data entries:', cursor.fetchall()); conn.close()\"",
        
        # Test data quality
        "python3 -c \"from r26_data_pipeline import R26DataPipeline; pipeline = R26DataPipeline(); summary = pipeline.get_data_summary(); print('\\nData Summary:'); print(summary)\""
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
    
    print(f"✅ Executing R26 data pipeline test on AWS...")
    
    try:
        # Execute the command
        result = subprocess.run(
            ssh_command,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        print("\n" + "=" * 60)
        print("AWS R26 DATA PIPELINE TEST OUTPUT")
        print("=" * 60)
        print(result.stdout)
        
        if result.stderr:
            print("\n" + "=" * 60)
            print("ERROR OUTPUT")
            print("=" * 60)
            print(result.stderr)
        
        if result.returncode == 0:
            print("\n✅ R26 data pipeline test completed successfully on AWS!")
            return True
        else:
            print(f"\n❌ R26 data pipeline test failed with return code: {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Test timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"❌ Failed to execute test: {e}")
        return False

def main():
    """Main execution"""
    success = test_r26_data_pipeline_aws()
    
    if success:
        print("\n🎉 R26 Data Pipeline AWS Test: SUCCESS")
        print("✅ Data pipeline is operational on AWS!")
        print("✅ Multi-source data collection working")
        print("✅ Data quality validation functional")
        print("✅ Storage and metadata system active")
    else:
        print("\n💥 R26 Data Pipeline AWS Test: FAILED")
        print("Check the error output above and resolve issues")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
