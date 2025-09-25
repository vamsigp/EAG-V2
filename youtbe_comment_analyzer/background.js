// Background script for Chrome extension
chrome.runtime.onInstalled.addListener(() => {
  console.log('YouTube Comment Analyzer installed');
});

// Handle messages from content script and popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'analyzeComments') {
    analyzeComments(request.comments)
      .then(response => sendResponse(response))
      .catch(error => sendResponse({ error: error.message }));
    return true; // Keep message channel open for async response
  }
  
  if (request.action === 'summarizeComments') {
    summarizeComments(request.comments)
      .then(response => sendResponse(response))
      .catch(error => sendResponse({ error: error.message }));
    return true;
  }
});

async function analyzeComments(comments) {
  console.log('🤖 Starting comment analysis...', { commentCount: comments.length });
  try {
    const { apiKey } = await chrome.storage.sync.get(['apiKey']);
    if (!apiKey) {
      console.error('❌ API key not found in storage');
      throw new Error('API key not configured. Please set your Gemini API key in the config.');
    }
    console.log('✅ API key found, preparing request...');

    const analysisPrompt = `
Analyze the following YouTube comments and classify each into one of three categories: "Good", "Bad", or "Neutral".
A "Good" comment is positive, constructive, helpful, or supportive.
A "Bad" comment is negative, toxic, spam, hateful, or unconstructive.
A "Neutral" comment is neither particularly positive nor negative.

Please respond with a JSON array where each object has "text" and "category" fields.

Comments to analyze:
${comments.map((comment, index) => `${index + 1}. ${comment}`).join('\n')}
`;

    console.log('📤 Sending request to Gemini API...', {
      endpoint: 'gemini-2.0-flash:generateContent',
      promptLength: analysisPrompt.length,
      commentsCount: comments.length
    });

    const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        contents: [{
          parts: [{
            text: analysisPrompt
          }]
        }]
      })
    });

    if (!response.ok) {
      console.error('❌ API request failed:', {
        status: response.status,
        statusText: response.statusText
      });
      throw new Error(`API request failed: ${response.status}`);
    }

    console.log('📥 Received response from Gemini API:', {
      status: response.status,
      statusText: response.statusText
    });

    const data = await response.json();
    console.log('🔍 Raw API response:', data);
    
    const analysisText = data.candidates[0].content.parts[0].text;
    console.log('📝 Analysis text received:', {
      textLength: analysisText.length,
      preview: analysisText.substring(0, 200) + '...'
    });
    
    // Try to parse JSON from the response
    let analysis;
    try {
      console.log('🔄 Parsing JSON response...');
      // Remove any markdown code blocks if present
      const jsonMatch = analysisText.match(/```json\n?(.*?)\n?```/s) || [null, analysisText];
      const jsonText = jsonMatch[1] || analysisText;
      console.log('📋 Extracted JSON text:', jsonText.substring(0, 300) + '...');
      
      analysis = JSON.parse(jsonText.trim());
      console.log('✅ Successfully parsed analysis:', {
        resultCount: analysis.length,
        categories: analysis.reduce((acc, item) => {
          acc[item.category] = (acc[item.category] || 0) + 1;
          return acc;
        }, {})
      });
    } catch (parseError) {
      console.warn('⚠️ Failed to parse JSON, using fallback:', parseError.message);
      // Fallback: classify all as neutral if parsing fails
      analysis = comments.map(comment => ({ text: comment, category: 'Neutral' }));
      console.log('🔄 Using fallback analysis:', { count: analysis.length });
    }

    console.log('🎉 Analysis completed successfully');
    return { success: true, analysis };
  } catch (error) {
    console.error('💥 Error analyzing comments:', {
      message: error.message,
      stack: error.stack,
      name: error.name
    });
    return { success: false, error: error.message };
  }
}

async function summarizeComments(comments) {
  console.log('📝 Starting comment summarization...', { totalComments: comments.length });
  try {
    const { apiKey } = await chrome.storage.sync.get(['apiKey']);
    if (!apiKey) {
      console.error('❌ API key not found for summarization');
      throw new Error('API key not configured. Please set your Gemini API key in the config.');
    }

    const top10Comments = comments.slice(0, 10);
    console.log('📊 Using top 10 comments for summary:', { count: top10Comments.length });
    const summaryPrompt = `
Summarize the following top 10 YouTube comments in 2-3 sentences. Focus on the main themes, opinions, and overall sentiment expressed by the viewers.

Comments:
${top10Comments.map((comment, index) => `${index + 1}. ${comment}`).join('\n')}
`;

    console.log('📤 Sending summarization request to Gemini API...', {
      endpoint: 'gemini-2.0-flash:generateContent',
      promptLength: summaryPrompt.length
    });

    const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        contents: [{
          parts: [{
            text: summaryPrompt
          }]
        }]
      })
    });

    if (!response.ok) {
      console.error('❌ Summarization API request failed:', {
        status: response.status,
        statusText: response.statusText
      });
      throw new Error(`API request failed: ${response.status}`);
    }

    console.log('📥 Received summarization response:', {
      status: response.status,
      statusText: response.statusText
    });

    const data = await response.json();
    console.log('🔍 Summary API response:', data);
    
    const summary = data.candidates[0].content.parts[0].text;
    console.log('📋 Generated summary:', {
      length: summary.length,
      preview: summary.substring(0, 100) + '...'
    });

    console.log('🎉 Summarization completed successfully');
    return { success: true, summary };
  } catch (error) {
    console.error('💥 Error summarizing comments:', {
      message: error.message,
      stack: error.stack,
      name: error.name
    });
    return { success: false, error: error.message };
  }
}