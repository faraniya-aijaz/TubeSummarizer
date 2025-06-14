from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
from api import gemini_api_key
import re

genai.configure(api_key=gemini_api_key)

def extract_video_id(url):
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    return match.group(1) if match else None

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = " ".join([item['text'] for item in transcript])
        return full_text
    except Exception as e:
        print(f"Error getting transcript: {e}")
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            transcript = transcript_list.find_transcript(['en', 'en-US', 'en-GB'])
            transcript_data = transcript.fetch()
            full_text = " ".join([item['text'] for item in transcript_data])
            return full_text
        except Exception as e2:
            print(f"No transcript available: {e2}")
            return None

def get_prompt_templates():
    return {
        "1": {
            "name": "Quick Summary",
            "prompt": """
            Create a concise summary of this YouTube video transcript in 3-4 bullet points:
            - Main topic/theme
            - Key points discussed
            - Important conclusion or takeaway
            
            Keep it brief and easy to read.
            
            Transcript: {text}
            """
        },
        "2": {
            "name": "Detailed Analysis",
            "prompt": """
            Provide a comprehensive analysis of this YouTube video transcript with the following structure:
            
            ## Overview
            Brief description of the video's main topic
            
            ## Key Points
            - List all major points discussed
            - Include supporting details and examples mentioned
            
            ## Important Quotes or Statistics
            - Highlight any significant quotes, numbers, or data mentioned
            
            ## Conclusion
            - Main takeaways
            - Actionable insights
            
            ## Target Audience
            Who would benefit most from this content?
            
            Transcript: {text}
            """
        },
        "3": {
            "name": "Educational Notes",
            "prompt": """
            Convert this YouTube video transcript into structured educational notes:
            
            ## Topic: [Main Subject]
            
            ## Learning Objectives
            What will viewers learn from this video?
            
            ## Key Concepts
            - Define and explain main concepts
            - Include examples and explanations
            
            ## Step-by-Step Process (if applicable)
            Break down any processes or methods explained
            
            ## Important Facts & Figures
            List key statistics, dates, or numerical data
            
            ## Summary Questions
            Create 3-5 questions that test understanding of the content
            
            Transcript: {text}
            """
        },
        "4": {
            "name": "Business/Professional Summary",
            "prompt": """
            Create a professional summary suitable for business contexts:
            
            ## Executive Summary
            One paragraph overview of the main topic and its relevance
            
            ## Key Business Insights
            - Strategic points that could impact business decisions
            - Market trends or opportunities mentioned
            - Competitive advantages or challenges discussed
            
            ## Actionable Recommendations
            What actions should be taken based on this content?
            
            ## ROI/Value Proposition
            What value does this information provide?
            
            ## Next Steps
            Suggested follow-up actions or further research needed
            
            Transcript: {text}
            """
        },
        "5": {
            "name": "Technical Deep Dive",
            "prompt": """
            Analyze this technical content with focus on:
            
            ## Technology/Method Overview
            What technology, method, or system is being discussed?
            
            ## Technical Specifications
            - Key technical details mentioned
            - Requirements or prerequisites
            - Performance metrics or benchmarks
            
            ## Implementation Details
            - Step-by-step technical process
            - Tools, software, or resources needed
            - Common challenges and solutions
            
            ## Pros and Cons
            Advantages and limitations discussed
            
            ## Use Cases
            Practical applications and scenarios
            
            ## Further Learning
            What additional knowledge might be needed?
            
            Transcript: {text}
            """
        },
        "6": {
            "name": "Creative/Content Summary",
            "prompt": """
            Summarize this creative or entertainment content:
            
            ## Content Type & Theme
            What type of content is this and what's the main theme?
            
            ## Creative Elements
            - Storytelling techniques used
            - Visual or audio elements mentioned
            - Creative decisions discussed
            
            ## Key Messages
            What messages or emotions is the creator trying to convey?
            
            ## Audience Engagement
            - How does the creator connect with their audience?
            - Interactive elements or calls-to-action
            
            ## Production Insights
            Behind-the-scenes information or creative process details
            
            ## Entertainment Value
            What makes this content engaging or entertaining?
            
            Transcript: {text}
            """
        },
        "7": {
            "name": "Research Summary",
            "prompt": """
            Create an academic-style research summary:
            
            ## Research Question/Hypothesis
            What question is being addressed or what hypothesis is being tested?
            
            ## Methodology
            What methods, approaches, or frameworks are discussed?
            
            ## Key Findings
            - Main discoveries or results
            - Supporting evidence presented
            - Data or statistics mentioned
            
            ## Implications
            What do these findings mean for the field or society?
            
            ## Limitations
            What limitations or caveats are mentioned?
            
            ## Future Research
            What questions remain unanswered or need further investigation?
            
            ## Citations/References
            Any sources, studies, or experts mentioned
            
            Transcript: {text}
            """
        },
        "8": {
            "name": "Custom Prompt",
            "prompt": "custom"
        }
    }

def display_prompt_options():
    templates = get_prompt_templates()
    print("\n" + "="*60)
    print("CHOOSE SUMMARY TYPE")
    print("="*60)
    for key, value in templates.items():
        print(f"{key}. {value['name']}")
    print("="*60)

def get_custom_prompt():
    print("\nEnter your custom prompt (use {text} where you want the transcript inserted):")
    print("Example: 'Summarize this video about {text} in simple terms for beginners'")
    return input("Custom prompt: ")

def summarize_text(text, prompt_template):
    try:
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        
        if prompt_template == "custom":
            custom_prompt = get_custom_prompt()
            prompt = custom_prompt.format(text=text)
        else:
            prompt = prompt_template.format(text=text)
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating summary: {e}")
        return None

def clean_gemini_output(raw_text):
    if not raw_text:
        return "No summary available"
    
    # Keep markdown formatting for better readability
    cleaned = re.sub(r"\n{3,}", "\n\n", raw_text).strip()
    return cleaned

def save_summary_to_file(summary, video_id, summary_type):
    """Save the summary to a text file"""
    try:
        filename = f"summary_{video_id}_{summary_type.replace(' ', '_').lower()}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"✅ Summary saved to: {filename}")
    except Exception as e:
        print(f"❌ Error saving file: {e}")

if __name__ == "__main__":
    # Check if API key is set
    if gemini_api_key == "":
        print("❌ Please set your actual Gemini API key in api.py")
        exit(1)
    
    print("🎥 YouTube Video Transcript Summarizer")
    print("="*50)
    
    youtube_url = input("Enter the YouTube URL: ")
    video_id = extract_video_id(youtube_url)
    
    if not video_id:
        print("❌ Invalid YouTube URL format")
        print("Expected formats:")
        print("- https://www.youtube.com/watch?v=VIDEO_ID")
        print("- https://youtu.be/VIDEO_ID")
    else:
        print(f"✅ Video ID extracted: {video_id}")
        
        transcript = get_transcript(video_id)
        if transcript:
            print("✅ Transcript retrieved successfully")
            print(f"📝 Transcript length: {len(transcript)} characters")
            
            # Show prompt options
            display_prompt_options()
            
            choice = input("\nSelect summary type (1-8): ").strip()
            templates = get_prompt_templates()
            
            if choice in templates:
                selected_template = templates[choice]
                print(f"\n🔄 Generating {selected_template['name']}...")
                
                summary = summarize_text(transcript, selected_template['prompt'])
                if summary:
                    formatted_summary = clean_gemini_output(summary)
                    print("\n" + "="*60)
                    print(f"📋 {selected_template['name'].upper()}")
                    print("="*60)
                    print(formatted_summary)
                    print("="*60)
                    
                    # Ask if user wants to save to file
                    save_choice = input("\n💾 Save summary to file? (y/n): ").lower()
                    if save_choice == 'y':
                        save_summary_to_file(formatted_summary, video_id, selected_template['name'])
                    
                    # Ask if user wants another summary type
                    another = input("\n🔄 Generate another type of summary? (y/n): ").lower()
                    if another == 'y':
                        display_prompt_options()
                        choice2 = input("Select another summary type (1-8): ").strip()
                        if choice2 in templates and choice2 != choice:
                            selected_template2 = templates[choice2]
                            print(f"\n🔄 Generating {selected_template2['name']}...")
                            summary2 = summarize_text(transcript, selected_template2['prompt'])
                            if summary2:
                                formatted_summary2 = clean_gemini_output(summary2)
                                print("\n" + "="*60)
                                print(f"📋 {selected_template2['name'].upper()}")
                                print("="*60)
                                print(formatted_summary2)
                                print("="*60)
                else:
                    print("❌ Failed to generate summary")
            else:
                print("❌ Invalid choice. Please select 1-8.")
        else:
            print("❌ Could not retrieve transcript for this video")
    
    print("\n👋 Thank you for using TubeSummarizer!")