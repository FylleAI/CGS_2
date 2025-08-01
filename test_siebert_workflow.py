#!/usr/bin/env python3
"""
Test script for the complete Siebert Premium Newsletter workflow.

This script tests the optimized workflow with Perplexity integration
to ensure everything works correctly end-to-end.
"""

import asyncio
import os
import sys
import logging
import json
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.abspath('.'))

# Import the handler to register it
from core.infrastructure.workflows.handlers.siebert_premium_newsletter_handler import SiebertPremiumNewsletterHandler
from core.infrastructure.workflows.registry import execute_dynamic_workflow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_siebert_workflow():
    """Test the complete Siebert premium newsletter workflow."""
    logger.info("🚀 Starting Siebert Premium Newsletter Workflow Test")
    logger.info("=" * 70)
    
    # Test context - realistic newsletter scenario
    test_context = {
        'topic': 'AI investment opportunities for young investors',
        'target_audience': 'Gen Z investors and young professionals interested in AI technology',
        'target_word_count': 1000,
        'edition_number': 1,
        'cultural_trends': 'TikTok AI content, ChatGPT popularity, tech job market',
        'exclude_topics': ['crypto day trading', 'get rich quick schemes'],
        'custom_instructions': 'Focus on accessible AI investment strategies for beginners',
        'client_name': 'siebert'
    }
    
    logger.info("📋 Test Context:")
    for key, value in test_context.items():
        logger.info(f"  {key}: {value}")
    
    try:
        logger.info("\n🔄 Executing Siebert Premium Newsletter Workflow...")
        
        # Execute the workflow
        result = await execute_dynamic_workflow('siebert_premium_newsletter', test_context)
        
        logger.info("✅ Workflow execution completed!")
        
        # Analyze results
        logger.info("\n📊 WORKFLOW RESULTS ANALYSIS:")
        logger.info("-" * 50)
        
        # Check workflow summary
        if 'workflow_summary' in result:
            summary = result['workflow_summary']
            logger.info(f"📄 Newsletter Topic: {summary.get('newsletter_topic', 'N/A')}")
            logger.info(f"👥 Target Audience: {summary.get('target_audience', 'N/A')}")
            logger.info(f"📏 Target Word Count: {summary.get('target_word_count', 'N/A')}")
            logger.info(f"📏 Final Word Count: {summary.get('final_word_count', 'N/A')}")
            logger.info(f"🎯 Word Count Accuracy: {summary.get('word_count_accuracy', 0):.1f}%")
            logger.info(f"🔍 Perplexity Integration: {summary.get('perplexity_integration', False)}")
            logger.info(f"🎨 Cultural Integration: {summary.get('cultural_integration', False)}")
            logger.info(f"📋 Siebert Format Applied: {summary.get('quality_indicators', {}).get('siebert_format', False)}")
        
        # Check task outputs
        task_outputs = []
        for key, value in result.items():
            if key.endswith('_output') and isinstance(value, str):
                task_outputs.append((key, len(value)))
        
        logger.info(f"\n📝 Task Outputs Found: {len(task_outputs)}")
        for task_name, length in task_outputs:
            logger.info(f"  - {task_name}: {length} characters")
        
        # Check final output
        if 'final_output' in result:
            final_content = result['final_output']
            word_count = len(final_content.split())
            logger.info(f"\n📄 Final Newsletter:")
            logger.info(f"  - Length: {len(final_content)} characters")
            logger.info(f"  - Word Count: {word_count} words")
            logger.info(f"  - Preview: {final_content[:200]}...")
            
            # Check for 8-section structure
            sections_found = []
            section_indicators = [
                "Community Greeting", "Hey Future Wealth Builders", "Hey Financial Futures",
                "Feature Story", "Market Reality Check", "By The Numbers",
                "Your Move This Week", "Community Corner", "Quick Links", "Stay empowered"
            ]
            
            for indicator in section_indicators:
                if indicator.lower() in final_content.lower():
                    sections_found.append(indicator)
            
            logger.info(f"  - Sections Found: {len(sections_found)}")
            for section in sections_found:
                logger.info(f"    ✓ {section}")
        
        # Quality assessment
        logger.info("\n🏆 QUALITY ASSESSMENT:")
        logger.info("-" * 30)
        
        quality_score = 0
        total_checks = 6
        
        # Check 1: Workflow completed
        if 'final_output' in result:
            quality_score += 1
            logger.info("✅ Workflow completed successfully")
        else:
            logger.info("❌ Workflow did not complete")
        
        # Check 2: Word count in range
        if 'workflow_summary' in result:
            accuracy = result['workflow_summary'].get('word_count_accuracy', 0)
            if 90 <= accuracy <= 110:
                quality_score += 1
                logger.info(f"✅ Word count accuracy: {accuracy:.1f}%")
            else:
                logger.info(f"⚠️ Word count accuracy: {accuracy:.1f}% (outside 90-110% range)")
        
        # Check 3: Perplexity integration
        if result.get('workflow_summary', {}).get('perplexity_integration', False):
            quality_score += 1
            logger.info("✅ Perplexity integration successful")
        else:
            logger.info("❌ Perplexity integration failed")
        
        # Check 4: Cultural integration
        if result.get('workflow_summary', {}).get('cultural_integration', False):
            quality_score += 1
            logger.info("✅ Cultural integration applied")
        else:
            logger.info("❌ Cultural integration missing")
        
        # Check 5: Siebert format
        if result.get('workflow_summary', {}).get('quality_indicators', {}).get('siebert_format', False):
            quality_score += 1
            logger.info("✅ Siebert 8-section format applied")
        else:
            logger.info("❌ Siebert format not properly applied")
        
        # Check 6: Content quality
        if 'final_output' in result and len(result['final_output']) > 500:
            quality_score += 1
            logger.info("✅ Substantial content generated")
        else:
            logger.info("❌ Insufficient content generated")
        
        # Final score
        percentage = (quality_score / total_checks) * 100
        logger.info(f"\n🎯 OVERALL QUALITY SCORE: {quality_score}/{total_checks} ({percentage:.1f}%)")
        
        if percentage >= 80:
            logger.info("🎉 EXCELLENT! Workflow is ready for production")
        elif percentage >= 60:
            logger.info("👍 GOOD! Minor improvements needed")
        else:
            logger.info("⚠️ NEEDS WORK! Significant issues to address")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Workflow test failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None


async def main():
    """Run the complete workflow test."""
    # Check environment
    if not os.getenv("PERPLEXITY_API_KEY"):
        logger.error("❌ PERPLEXITY_API_KEY not set in environment")
        logger.info("💡 Set with: export PERPLEXITY_API_KEY=your_key_here")
        return
    
    # Run test
    result = await test_siebert_workflow()
    
    if result:
        logger.info("\n" + "=" * 70)
        logger.info("🏁 TEST COMPLETED SUCCESSFULLY")
        logger.info("=" * 70)
        
        # Save result for inspection
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"siebert_workflow_test_result_{timestamp}.json"
        
        # Prepare result for JSON serialization
        json_result = {}
        for key, value in result.items():
            if isinstance(value, (str, int, float, bool, list, dict)):
                json_result[key] = value
            else:
                json_result[key] = str(value)
        
        with open(output_file, 'w') as f:
            json.dump(json_result, f, indent=2)
        
        logger.info(f"📁 Full results saved to: {output_file}")
    else:
        logger.error("💥 TEST FAILED - Check logs above for details")


if __name__ == "__main__":
    # Set environment variable for test
    os.environ["PERPLEXITY_API_KEY"] = "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"
    
    # Run test
    asyncio.run(main())
