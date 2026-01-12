-- Add AI Chatbot features to competitive comparison matrix
-- Run in Supabase SQL Editor

INSERT INTO feature_comparisons (feature_category, feature_name, gridics_has, zonewise_has, gridics_quality, zonewise_quality, competitive_advantage, priority, notes) VALUES

-- AI Chatbot Category (NEW)
('ai_chatbot', 'Natural Language Input', FALSE, TRUE, 'unknown', 'excellent', 'zonewise', 'critical', 'ZoneWise allows plain English questions like "Can I build apartments in Melbourne?"'),
('ai_chatbot', 'Conversational Interface', FALSE, TRUE, 'unknown', 'excellent', 'zonewise', 'critical', 'ZoneWise has chat interface vs Gridics form-based search'),
('ai_chatbot', 'Context Awareness', FALSE, TRUE, 'unknown', 'excellent', 'zonewise', 'high', 'ZoneWise remembers previous questions in conversation'),
('ai_chatbot', 'Intent Recognition', FALSE, TRUE, 'unknown', 'excellent', 'zonewise', 'high', 'ZoneWise AI understands 6 intent types (feasibility, calculation, comparison, process, research, definition)'),
('ai_chatbot', 'Follow-up Suggestions', FALSE, TRUE, 'unknown', 'excellent', 'zonewise', 'medium', 'ZoneWise suggests next steps intelligently'),
('ai_chatbot', 'Educational Explanations', FALSE, TRUE, 'unknown', 'excellent', 'zonewise', 'medium', 'ZoneWise explains zoning concepts in conversation'),
('ai_chatbot', 'Voice Input', FALSE, FALSE, 'unknown', 'unknown', 'neutral', 'low', 'Neither has voice input yet (ZoneWise roadmap Q3 2026)'),
('ai_chatbot', 'Multi-Modal Responses', FALSE, TRUE, 'unknown', 'excellent', 'zonewise', 'high', 'ZoneWise provides text + structured data + visualizations'),
('ai_chatbot', 'Zero Learning Curve', FALSE, TRUE, 'unknown', 'excellent', 'zonewise', 'critical', 'Anyone can use ZoneWise without zoning knowledge'),
('ai_chatbot', '24/7 AI Assistant', FALSE, TRUE, 'unknown', 'excellent', 'zonewise', 'high', 'ZoneWise chatbot always available')

ON CONFLICT DO NOTHING;

-- Update existing search feature to highlight chatbot advantage
UPDATE feature_comparisons 
SET notes = 'ZoneWise has AI chatbot with natural language search vs Gridics basic keyword search'
WHERE feature_name = 'Address Search' AND feature_category = 'search';

-- View updated competitive advantage summary
SELECT * FROM feature_advantage_summary;
