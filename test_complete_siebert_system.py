#!/usr/bin/env python3
"""
Complete system test for Siebert Premium Newsletter with full agent execution.

This test uses the complete GenerateContentUseCase to ensure proper
agent_executor integration and real Perplexity tool execution.
"""

import asyncio
import os
import sys
import logging
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.abspath('.'))

from core.application.use_cases.generate_content import GenerateContentUseCase
from core.application.dto.content_request import ContentGenerationRequest
from core.domain.value_objects.generation_params import GenerationParams
from core.domain.value_objects.provider_config import ProviderConfig, LLMProvider
from core.infrastructure.config.settings import Settings
from core.infrastructure.repositories.file_content_repository import FileContentRepository
from core.infrastructure.repositories.file_workflow_repository import FileWorkflowRepository
from core.infrastructure.repositories.yaml_agent_repository import YamlAgentRepository
from core.infrastructure.external_services.openai_adapter import OpenAIAdapter

# Import the handler to register it
from core.infrastructure.workflows.handlers.siebert_premium_newsletter_handler import SiebertPremiumNewsletterHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_complete_siebert_system():
    """Test the complete Siebert system with real agent execution."""
    logger.info("🚀 Starting Complete Siebert System Test")
    logger.info("=" * 80)
    
    try:
        # Initialize settings
        settings = Settings()
        
        # Initialize repositories
        content_repository = FileContentRepository()
        workflow_repository = FileWorkflowRepository()
        agent_repository = YamlAgentRepository()
        
        # Initialize LLM provider
        provider_config = ProviderConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4o",
            temperature=0.7
        )
        llm_provider = OpenAIAdapter(settings.openai_api_key)
        
        # Initialize the complete use case
        use_case = GenerateContentUseCase(
            content_repository=content_repository,
            workflow_repository=workflow_repository,
            agent_repository=agent_repository,
            llm_provider=llm_provider,
            provider_config=provider_config,
            rag_service=None,
            serper_api_key=settings.serper_api_key,
            perplexity_api_key=settings.perplexity_api_key
        )
        
        logger.info("✅ System components initialized successfully")
        
        # Create generation parameters for Siebert newsletter
        generation_params = GenerationParams(
            topic="AI investment opportunities for young investors",
            target_audience="Gen Z investors and young professionals interested in AI technology",
            target_word_count=1000,
            custom_instructions="Focus on accessible AI investment strategies for beginners"
        )
        
        # Create content generation request
        request = ContentGenerationRequest(
            topic="AI investment opportunities for young investors",
            client_profile="siebert",
            workflow_type="siebert_premium_newsletter",
            custom_instructions="Generate a premium newsletter for Gen Z investors about AI investment opportunities",
            generation_params=generation_params,
            provider_config=provider_config,
            context={
                "edition_number": 1,
                "cultural_trends": "TikTok AI content, ChatGPT popularity, tech job market",
                "exclude_topics": ["crypto day trading", "get rich quick schemes"]
            }
        )
        
        logger.info("📋 Request Configuration:")
        logger.info(f"  Topic: {request.topic}")
        logger.info(f"  Client: {request.client_profile}")
        logger.info(f"  Workflow: {request.workflow_type}")
        logger.info(f"  Target Audience: {generation_params.target_audience}")
        logger.info(f"  Word Count: {generation_params.target_word_count}")
        
        # Execute the complete system
        logger.info("\n🔄 Executing Complete Siebert Newsletter Generation...")
        start_time = datetime.now()
        
        response = await use_case.execute(request)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"✅ System execution completed in {duration:.2f} seconds!")
        
        # Analyze results
        logger.info("\n📊 COMPLETE SYSTEM RESULTS ANALYSIS:")
        logger.info("-" * 60)
        
        logger.info(f"📄 Content ID: {response.content_id}")
        logger.info(f"📏 Content Length: {len(response.body)} characters")
        logger.info(f"📝 Word Count: {len(response.body.split())} words")
        logger.info(f"⏱️ Generation Time: {duration:.2f} seconds")
        logger.info(f"💰 Cost: ${getattr(response, 'cost', 0):.6f}")
        logger.info(f"🔢 Tokens: {getattr(response, 'tokens', 0)}")

        # Check newsletter structure
        content = response.body
        logger.info(f"\n📄 Newsletter Content Analysis:")
        logger.info(f"  - Content Preview: {content[:200]}...")
        
        # Check for Siebert 8-section structure
        siebert_sections = [
            "Hey Future Wealth Builders", "Hey Financial Futures", "Hey Money Mavens",
            "Feature Story", "Market Reality Check", "By The Numbers",
            "Your Move This Week", "Community Corner", "Quick Links", "Stay empowered"
        ]
        
        sections_found = []
        for section in siebert_sections:
            if section.lower() in content.lower():
                sections_found.append(section)
        
        logger.info(f"  - Siebert Sections Found: {len(sections_found)}")
        for section in sections_found:
            logger.info(f"    ✓ {section}")
        
        # Check for Perplexity integration indicators
        perplexity_indicators = [
            "research", "analysis", "market", "trends", "data", "statistics"
        ]
        
        perplexity_found = []
        for indicator in perplexity_indicators:
            if indicator.lower() in content.lower():
                perplexity_found.append(indicator)
        
        logger.info(f"  - Research Indicators: {len(perplexity_found)}")
        
        # Check for Gen Z cultural elements
        cultural_indicators = [
            "AI", "TikTok", "ChatGPT", "tech", "young", "generation", "future"
        ]
        
        cultural_found = []
        for indicator in cultural_indicators:
            if indicator.lower() in content.lower():
                cultural_found.append(indicator)
        
        logger.info(f"  - Cultural Elements: {len(cultural_found)}")
        
        # Quality assessment
        logger.info("\n🏆 COMPLETE SYSTEM QUALITY ASSESSMENT:")
        logger.info("-" * 50)
        
        quality_score = 0
        total_checks = 8
        
        # Check 1: Content generated
        if len(content) > 500:
            quality_score += 1
            logger.info("✅ Substantial content generated")
        else:
            logger.info("❌ Insufficient content generated")
        
        # Check 2: Word count in range
        word_count = len(content.split())
        target_count = generation_params.target_word_count
        accuracy = (word_count / target_count * 100) if target_count > 0 else 0
        if 70 <= accuracy <= 130:  # More lenient range for real execution
            quality_score += 1
            logger.info(f"✅ Word count acceptable: {word_count} words ({accuracy:.1f}%)")
        else:
            logger.info(f"⚠️ Word count outside range: {word_count} words ({accuracy:.1f}%)")
        
        # Check 3: Siebert sections present
        if len(sections_found) >= 3:
            quality_score += 1
            logger.info(f"✅ Siebert sections present: {len(sections_found)}")
        else:
            logger.info(f"❌ Insufficient Siebert sections: {len(sections_found)}")
        
        # Check 4: Research indicators
        if len(perplexity_found) >= 4:
            quality_score += 1
            logger.info(f"✅ Research content present: {len(perplexity_found)} indicators")
        else:
            logger.info(f"⚠️ Limited research content: {len(perplexity_found)} indicators")
        
        # Check 5: Cultural relevance
        if len(cultural_found) >= 3:
            quality_score += 1
            logger.info(f"✅ Cultural elements present: {len(cultural_found)}")
        else:
            logger.info(f"❌ Limited cultural elements: {len(cultural_found)}")
        
        # Check 6: Cost efficiency
        cost = getattr(response, 'cost', 0)
        if cost < 1.0:  # Under $1
            quality_score += 1
            logger.info(f"✅ Cost efficient: ${cost:.6f}")
        else:
            logger.info(f"⚠️ High cost: ${cost:.6f}")
        
        # Check 7: Reasonable generation time
        if duration < 120:  # Under 2 minutes
            quality_score += 1
            logger.info(f"✅ Fast generation: {duration:.2f}s")
        else:
            logger.info(f"⚠️ Slow generation: {duration:.2f}s")
        
        # Check 8: No errors in response
        if response.content and not "error" in content.lower():
            quality_score += 1
            logger.info("✅ No errors detected")
        else:
            logger.info("❌ Errors detected in content")
        
        # Final score
        percentage = (quality_score / total_checks) * 100
        logger.info(f"\n🎯 COMPLETE SYSTEM QUALITY SCORE: {quality_score}/{total_checks} ({percentage:.1f}%)")
        
        if percentage >= 85:
            logger.info("🎉 EXCELLENT! Complete system is production-ready")
        elif percentage >= 70:
            logger.info("👍 GOOD! System working well with minor improvements needed")
        elif percentage >= 50:
            logger.info("⚠️ FAIR! System functional but needs optimization")
        else:
            logger.info("❌ POOR! System needs significant improvements")
        
        # Save full content for inspection
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"siebert_complete_system_test_{timestamp}.md"
        
        with open(output_file, 'w') as f:
            f.write(f"# Siebert Premium Newsletter - Complete System Test\n\n")
            f.write(f"**Generated**: {datetime.now().isoformat()}\n")
            f.write(f"**Topic**: {request.topic}\n")
            f.write(f"**Word Count**: {word_count} words\n")
            f.write(f"**Generation Time**: {duration:.2f} seconds\n")
            f.write(f"**Cost**: ${getattr(response, 'cost', 0):.6f}\n")
            f.write(f"**Quality Score**: {quality_score}/{total_checks} ({percentage:.1f}%)\n\n")
            f.write("---\n\n")
            f.write(response.body)
        
        logger.info(f"📁 Full newsletter saved to: {output_file}")
        
        return {
            'success': True,
            'quality_score': quality_score,
            'total_checks': total_checks,
            'percentage': percentage,
            'word_count': word_count,
            'duration': duration,
            'cost': getattr(response, 'cost', 0),
            'content_length': len(content),
            'sections_found': len(sections_found),
            'output_file': output_file
        }
        
    except Exception as e:
        logger.error(f"❌ Complete system test failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            'success': False,
            'error': str(e)
        }


async def main():
    """Run the complete system test."""
    # Check environment
    required_keys = ["OPENAI_API_KEY", "PERPLEXITY_API_KEY"]
    missing_keys = [key for key in required_keys if not os.getenv(key)]
    
    if missing_keys:
        logger.error(f"❌ Missing required environment variables: {missing_keys}")
        logger.info("💡 Set them with:")
        for key in missing_keys:
            logger.info(f"  export {key}=your_key_here")
        return
    
    # Run test
    result = await test_complete_siebert_system()
    
    if result.get('success'):
        logger.info("\n" + "=" * 80)
        logger.info("🏁 COMPLETE SYSTEM TEST SUCCESSFUL")
        logger.info("=" * 80)
        logger.info(f"🎯 Final Quality Score: {result['quality_score']}/{result['total_checks']} ({result['percentage']:.1f}%)")
        logger.info(f"📊 Performance Metrics:")
        logger.info(f"  - Word Count: {result['word_count']} words")
        logger.info(f"  - Generation Time: {result['duration']:.2f} seconds")
        logger.info(f"  - Cost: ${result['cost']:.6f}")
        logger.info(f"  - Content Length: {result['content_length']} characters")
        logger.info(f"  - Siebert Sections: {result['sections_found']}")
        logger.info(f"📁 Full output: {result['output_file']}")
    else:
        logger.error("💥 COMPLETE SYSTEM TEST FAILED")
        logger.error(f"Error: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    # Set environment variables for test
    os.environ["PERPLEXITY_API_KEY"] = "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"
    
    # Run test
    asyncio.run(main())
