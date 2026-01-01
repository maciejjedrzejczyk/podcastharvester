# AI Summarization

This guide covers the AI-powered content summarization system in PodcastHarvester, including setup, configuration, and workflow details.

## Overview

PodcastHarvester's AI summarization system processes video transcripts through a multi-stage workflow:

1. **Transcript Processing** - Parse SRT subtitle files
2. **Content Chunking** - Split into 5-minute segments
3. **Chunk Summarization** - Generate individual summaries via LLM
4. **Final Summarization** - Create comprehensive video summary

## LLM Server Setup

### Supported LLM Backends

**Local Servers:**
- **Ollama** - `http://localhost:11434`
- **LM Studio** - `http://localhost:1234`
- **Text Generation WebUI** - `http://localhost:5000`

**Cloud Services:**
- **OpenAI-compatible APIs**
- **Custom endpoints**

### Configuration

Create `llm_config.json`:

```json
{
  "server_url": "http://localhost:1234",
  "model_name": "llama-3.1-8b-instruct",
  "context_length": 4096,
  "temperature": 0.7,
  "system_prompts": {
    "chunk": "You are an expert content analyst...",
    "final": "You are an expert content analyst tasked with creating comprehensive final summaries..."
  },
  "request_timeout": 60,
  "max_retries": 3,
  "retry_delay": 2
}
```

### LLM Server Installation

**Ollama Setup:**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama3.1:8b

# Start server (runs on localhost:11434)
ollama serve
```

**LM Studio Setup:**
1. Download and install LM Studio
2. Download a compatible model (e.g., Llama 3.1 8B)
3. Start local server on port 1234
4. Configure model settings

## Summarization Workflow

### 1. Transcript Processing

The system looks for subtitle files in video folders:
- **Primary**: `video_name.en.srt` (English subtitles)
- **Fallback**: Any `.srt` file in the folder
- **Auto-generated**: Supports YouTube's auto-generated subtitles

### 2. Content Chunking

Transcripts are split into 5-minute segments:
- **Chunk duration**: 300 seconds (configurable)
- **Timestamp preservation**: Maintains original timing
- **Text consolidation**: Combines subtitle entries within timeframe

**Chunk Structure:**
```json
{
  "chunk_number": 1,
  "start_time": 0,
  "end_time": 300,
  "text": "Combined transcript text for 5-minute segment..."
}
```

### 3. Individual Chunk Summarization

Each chunk is processed independently:
- **LLM prompt**: Uses "chunk" system prompt from configuration
- **Context preservation**: Maintains video context
- **Error handling**: Retries failed requests with exponential backoff

**Output**: `chunk_summaries/chunk_001_summary.txt`

### 4. Final Summary Generation

All chunk summaries are combined:
- **LLM prompt**: Uses "final" system prompt from configuration
- **Comprehensive analysis**: Synthesizes all chunk information
- **Structured output**: Creates cohesive final summary

**Output**: `content_summary/summary.txt`

## Directory Structure

After summarization, each video folder contains:

```
video_folder/
├── video_file.mp3
├── video_file.en.srt          # Source transcript
├── chunks/                    # 5-minute segments
│   ├── chunk_001.txt
│   ├── chunk_002.txt
│   └── chunk_003.txt
├── chunk_summaries/           # Individual summaries
│   ├── chunk_001_summary.txt
│   ├── chunk_002_summary.txt
│   └── chunk_003_summary.txt
└── content_summary/           # Final output
    ├── summary.txt            # Final summary
    └── metadata.json          # Processing metadata
```

## Configuration Options

### Channel-Level Configuration

Enable summarization per channel in `channels_config.json`:

```json
{
  "channel_name": "Example Channel",
  "summarize": "yes",           # Enable AI summarization
  "transcript_languages": ["en", "es"],  # Required for summarization
  "download_transcript": true   # Must be true for summarization
}
```

### System Prompts

Customize AI behavior by modifying system prompts in `llm_config.json`:

**Chunk Prompt** (for individual segments):
```json
{
  "chunk": "You are an expert content analyst specializing in creating concise, informative summaries of video transcript segments. Focus on:\n\n1. Main topics and themes discussed\n2. Key arguments, evidence, or data presented\n3. Important conclusions or insights\n4. Notable quotes or statements\n5. Any actionable information or recommendations\n\nCreate a clear, well-structured summary that captures the essence of the content while being concise and easy to understand."
}
```

**Final Prompt** (for comprehensive summary):
```json
{
  "final": "You are an expert content analyst tasked with creating comprehensive final summaries from multiple chunk summaries of a video. Synthesize all chunk summaries into a cohesive overview that captures:\n\n1. Overall theme and main topic of the video\n2. Key arguments and supporting evidence\n3. Major conclusions and insights\n4. Important facts, data, or statistics\n5. Progression of ideas and logical flow\n6. Actionable takeaways or recommendations\n\nCreate a well-structured final summary that provides complete understanding of the video's content."
}
```

## Usage

### Automatic Summarization

Summarization runs automatically after content harvesting:

```bash
# Process channels with summarization enabled
python3 podcast_harvester.py --config channels_config.json
```

### Manual Summarization

Run summarization independently:

```bash
# Summarize all channels with summarize="yes"
python3 content_summarizer.py --config channels_config.json

# Summarize specific channels only
python3 content_summarizer.py --config channels_config.json --channels "Channel1,Channel2"

# Summarize specific video folder
python3 content_summarizer.py --video-folder "downloads/Channel/Video_Folder"
```

### Web Interface

Use the web interface for ad-hoc summarization:
1. Open http://localhost:8080
2. Navigate to Settings → Process URL
3. Enter YouTube URL with summarization enabled
4. Monitor progress in real-time

## Monitoring and Troubleshooting

### Progress Tracking

The system provides detailed progress information:
- **Chunk processing**: Individual chunk completion status
- **LLM requests**: Request/response timing and status
- **Error handling**: Detailed error messages and retry attempts

### Common Issues

**LLM Server Connection:**
```bash
# Test LLM server connectivity
curl -X POST http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"your-model","messages":[{"role":"user","content":"test"}]}'
```

**Missing Transcripts:**
- Ensure `download_transcript: true` in channel configuration
- Check `transcript_languages` includes available languages
- Verify subtitle files exist in video folders

**Memory Issues:**
- Reduce `context_length` in LLM configuration
- Use smaller models for resource-constrained systems
- Process fewer channels simultaneously

### Metadata Tracking

Each summarized video includes processing metadata:

```json
{
  "processing_date": "2025-01-01T12:00:00",
  "llm_config": {
    "server_url": "http://localhost:1234",
    "model_name": "llama-3.1-8b-instruct"
  },
  "chunk_count": 5,
  "processing_time_seconds": 120,
  "transcript_language": "en",
  "chunk_summaries_generated": 5,
  "final_summary_generated": true
}
```

## Performance Optimization

### LLM Server Optimization
- **Model selection**: Balance quality vs. speed
- **Context length**: Optimize for your content length
- **Temperature**: Lower values for more consistent summaries
- **Batch processing**: Process multiple videos sequentially

### System Resources
- **Memory**: Ensure adequate RAM for chosen model
- **CPU/GPU**: Utilize hardware acceleration when available
- **Storage**: Monitor disk space for chunk and summary files
- **Network**: Stable connection for cloud-based LLMs

### Processing Strategies
- **Selective summarization**: Enable only for important channels
- **Batch processing**: Process multiple videos in single session
- **Retry logic**: Automatic handling of temporary failures
- **Progress persistence**: Resume interrupted processing

## Integration with Other Features

### Web Interface Integration
- Real-time progress display
- Summary viewing and management
- Configuration management
- Error reporting and diagnostics

### RSS Feed Integration
- Summaries included in RSS feed descriptions
- Enhanced metadata for podcast managers
- Automatic feed updates after summarization

### Notification Integration
- Completion notifications with summary statistics
- Error notifications for failed processing
- Custom webhook payloads with summary information
