#!/usr/bin/env python3
"""
Generate Interactive HTML Viewer for YouTube Channels
Creates a beautiful, filterable, sortable view of all channels with clickable links
"""

import json
from channel_database import ChannelDatabase
from typing import List, Dict

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YouTube Channels Database</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        :root {{
            --bg-primary: #0a0a0a;
            --bg-secondary: #1a1a1a;
            --bg-tertiary: #222222;
            --border-color: #2a2a2a;
            --text-primary: #e5e5e5;
            --text-secondary: #9a9a9a;
            --text-tertiary: #6a6a6a;
            --accent-blue: #4a9eff;
            --accent-blue-hover: #5eaeff;
            --success-green: #4ade80;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            letter-spacing: 0.01em;
            min-height: 100vh;
            padding: 40px 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        header {{
            margin-bottom: 48px;
            padding-bottom: 24px;
            border-bottom: 1px solid var(--border-color);
        }}
        
        h1 {{
            font-size: 32px;
            font-weight: 500;
            margin-bottom: 8px;
            letter-spacing: -0.02em;
            color: var(--text-primary);
        }}
        
        .subtitle {{
            color: var(--text-secondary);
            font-size: 16px;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 16px;
            margin: 24px 0;
        }}
        
        .stat-box {{
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 4px;
            padding: 20px;
            transition: border-color 0.2s ease;
        }}
        
        .stat-box:hover {{
            border-color: #3a3a3a;
        }}
        
        .stat-number {{
            font-size: 28px;
            font-weight: 500;
            color: var(--text-primary);
            margin-bottom: 4px;
        }}
        
        .stat-label {{
            font-size: 13px;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .controls {{
            display: flex;
            gap: 12px;
            margin: 32px 0;
            flex-wrap: wrap;
            align-items: center;
        }}
        
        input[type="text"], select {{
            padding: 12px 14px;
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 3px;
            font-size: 14px;
            color: var(--text-primary);
            font-family: inherit;
            flex: 1;
            min-width: 200px;
            transition: border-color 0.2s ease, background 0.2s ease;
        }}
        
        input[type="text"]:focus, select:focus {{
            outline: none;
            border-color: var(--accent-blue);
            background: var(--bg-tertiary);
        }}
        
        input[type="text"]::placeholder {{
            color: var(--text-tertiary);
        }}
        
        button {{
            padding: 12px 20px;
            background: var(--bg-secondary);
            color: var(--text-primary);
            border: 1px solid var(--border-color);
            border-radius: 3px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: border-color 0.2s ease, background 0.2s ease;
        }}
        
        button:hover {{
            border-color: var(--accent-blue);
            background: var(--bg-tertiary);
        }}
        
        .channels-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
            gap: 16px;
            margin: 24px 0;
        }}
        
        .channel-card {{
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 4px;
            padding: 20px;
            transition: border-color 0.2s ease;
        }}
        
        .channel-card:hover {{
            border-color: #3a3a3a;
        }}
        
        .channel-header {{
            margin-bottom: 16px;
        }}
        
        .channel-name {{
            font-size: 18px;
            font-weight: 500;
            margin-bottom: 8px;
        }}
        
        .channel-name a {{
            color: var(--accent-blue);
            text-decoration: none;
            transition: color 0.2s ease;
        }}
        
        .channel-name a:hover {{
            color: var(--accent-blue-hover);
        }}
        
        .channel-about-link {{
            display: inline-block;
            margin-left: 8px;
            padding: 4px 8px;
            background: var(--bg-primary);
            border: 1px solid var(--border-color);
            border-radius: 2px;
            text-decoration: none;
            color: var(--text-secondary);
            font-size: 12px;
            transition: border-color 0.2s ease;
        }}
        
        .channel-about-link:hover {{
            border-color: var(--accent-blue);
            color: var(--accent-blue);
        }}
        
        .subscriber-count {{
            font-size: 14px;
            color: var(--text-secondary);
            font-weight: 400;
            margin-bottom: 8px;
        }}
        
        .category-badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 2px;
            font-size: 11px;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .category-prepper {{
            background: rgba(74, 222, 128, 0.15);
            color: var(--success-green);
        }}
        
        .category-discovered,
        .category-ai_discovered {{
            background: rgba(74, 158, 255, 0.15);
            color: var(--accent-blue);
        }}
        
        .category-other {{
            background: rgba(154, 154, 154, 0.15);
            color: var(--text-secondary);
        }}
        
        .contacts {{
            margin-top: 16px;
            padding-top: 16px;
            border-top: 1px solid var(--border-color);
        }}
        
        .contact-item {{
            display: inline-flex;
            align-items: center;
            margin: 4px 8px 4px 0;
            padding: 6px 10px;
            background: var(--bg-primary);
            border: 1px solid var(--border-color);
            border-radius: 2px;
            font-size: 13px;
            text-decoration: none;
            color: var(--text-secondary);
            transition: border-color 0.2s ease, color 0.2s ease;
        }}
        
        .contact-item:hover {{
            border-color: var(--accent-blue);
            color: var(--accent-blue);
        }}
        
        .contact-icon {{
            margin-right: 6px;
        }}
        
        .no-contacts {{
            color: var(--text-tertiary);
            font-size: 13px;
        }}
        
        .empty-state {{
            text-align: center;
            padding: 80px 20px;
            color: var(--text-secondary);
            grid-column: 1 / -1;
        }}
        
        .empty-state-icon {{
            font-size: 48px;
            margin-bottom: 16px;
            opacity: 0.5;
        }}
        
        .empty-state h2 {{
            font-size: 20px;
            font-weight: 500;
            margin-bottom: 8px;
            color: var(--text-primary);
        }}
        
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: var(--bg-primary);
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: var(--border-color);
            border-radius: 4px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: #3a3a3a;
        }}
        
        @media (max-width: 768px) {{
            .channels-grid {{
                grid-template-columns: 1fr;
            }}
            
            .controls {{
                flex-direction: column;
            }}
            
            input[type="text"], select, button {{
                width: 100%;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>YouTube Channels Database</h1>
            <p class="subtitle">Discovered micro-influencers and outreach targets</p>
            
            <div class="stats">
                <div class="stat-box">
                    <div class="stat-number" id="total-channels">{{total_channels}}</div>
                    <div class="stat-label">Total Channels</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number" id="with-email">{{channels_with_email}}</div>
                    <div class="stat-label">With Email</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number" id="target-range">{{target_range}}</div>
                    <div class="stat-label">Target Range</div>
                </div>
            </div>
        </header>
        
        <div class="controls">
            <input type="text" id="search-input" placeholder="Search channels..." onkeyup="filterChannels()">
            <select id="category-filter" onchange="filterChannels()">
                <option value="">All Categories</option>
                <option value="prepper">Prepper</option>
                <option value="discovered">Discovered</option>
                <option value="ai_discovered">AI Discovered</option>
                <option value="other">Other</option>
            </select>
            <select id="sort-select" onchange="sortChannels()">
                <option value="subs-desc">Subscribers ↓</option>
                <option value="subs-asc">Subscribers ↑</option>
                <option value="name-asc">Name A-Z</option>
                <option value="name-desc">Name Z-A</option>
            </select>
            <button onclick="resetFilters()">Reset Filters</button>
        </div>
        
        <div class="channels-grid" id="channels-container">
            {{channels_html}}
        </div>
    </div>
    
    <script>
        let allChannels = {{channels_json}};
        
        function formatNumber(num) {
            if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
            if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
            return num.toString();
        }
        
        function renderChannels(channels) {
            const container = document.getElementById('channels-container');
            
            if (channels.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-state-icon">🔍</div>
                        <h2>No channels found</h2>
                        <p>Try adjusting your filters</p>
                    </div>
                `;
                return;
            }
            
            container.innerHTML = channels.map(channel => {
                const contactsHtml = channel.contacts && channel.contacts.length > 0
                    ? channel.contacts.map(contact => {
                        let icon, url, label;
                        switch(contact.contact_type) {
                            case 'email':
                                icon = '📧';
                                url = `mailto:${contact.contact_value}`;
                                label = contact.contact_value;
                                break;
                            case 'instagram':
                                icon = '📸';
                                url = `https://instagram.com/${contact.contact_value}`;
                                label = `@${contact.contact_value}`;
                                break;
                            case 'twitter':
                                icon = '🐦';
                                url = `https://twitter.com/${contact.contact_value}`;
                                label = `@${contact.contact_value}`;
                                break;
                            case 'facebook':
                                icon = '📘';
                                url = `https://facebook.com/${contact.contact_value}`;
                                label = contact.contact_value;
                                break;
                            default:
                                icon = '🌐';
                                url = `https://${contact.contact_value}`;
                                label = contact.contact_value;
                        }
                        return `<a href="${url}" target="_blank" class="contact-item">
                            <span class="contact-icon">${icon}</span> ${label}
                        </a>`;
                    }).join('')
                    : '<div class="no-contacts">No contact info yet - visit About page</div>';
                
                const aboutUrl = `${channel.channel_url}/about`;
                
                // Enhanced metrics display
                let metricsHtml = '';
                if (channel.engagement_rate || channel.view_rate || channel.growth_trend) {
                    const metrics = [];
                    
                    if (channel.engagement_rate) {
                        const engClass = channel.engagement_rate >= 5 ? 'success-green' : 'text-secondary';
                        metrics.push(`<div style="text-align: center;"><div style="color: var(--text-tertiary); font-size: 11px;">Engagement</div><div style="color: var(--${engClass}); font-weight: 500;">${channel.engagement_rate}%</div></div>`);
                    }
                    
                    if (channel.view_rate) {
                        const viewClass = channel.view_rate >= 30 ? 'success-green' : 'text-secondary';
                        metrics.push(`<div style="text-align: center;"><div style="color: var(--text-tertiary); font-size: 11px;">View Rate</div><div style="color: var(--${viewClass}); font-weight: 500;">${channel.view_rate}%</div></div>`);
                    }
                    
                    if (channel.avg_views_per_video) {
                        metrics.push(`<div style="text-align: center;"><div style="color: var(--text-tertiary); font-size: 11px;">Avg Views</div><div style="color: var(--text-primary); font-weight: 500;">${formatNumber(channel.avg_views_per_video)}</div></div>`);
                    }
                    
                    if (channel.growth_trend) {
                        const trendEmoji = {'rapid': '🚀', 'growing': '📈', 'stable': '➡️', 'declining': '📉'}[channel.growth_trend] || '➡️';
                        const trendClass = channel.growth_trend === 'rapid' || channel.growth_trend === 'growing' ? 'success-green' : 'text-secondary';
                        metrics.push(`<div style="text-align: center;"><div style="color: var(--text-tertiary); font-size: 11px;">Trend</div><div style="color: var(--${trendClass}); font-weight: 500;">${trendEmoji} ${channel.growth_trend}</div></div>`);
                    }
                    
                    metricsHtml = `<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(80px, 1fr)); gap: 8px; margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--border-color);">${metrics.join('')}</div>`;
                }
                
                return `
                    <div class="channel-card" data-category="${channel.category}" data-name="${channel.channel_name}" data-subs="${channel.subscriber_count}">
                        <div class="channel-header">
                            <div class="channel-name">
                                <a href="${channel.channel_url}" target="_blank">${channel.channel_name}</a>
                                <a href="${aboutUrl}" target="_blank" class="channel-about-link">About Page</a>
                            </div>
                            <div class="subscriber-count">
                                👥 ${formatNumber(channel.subscriber_count)} subscribers
                            </div>
                            <span class="category-badge category-${channel.category}">${channel.category}</span>
                        </div>
                        ${metricsHtml}
                        <div class="contacts">
                            ${contactsHtml}
                        </div>
                    </div>
                `;
            }).join('');
        }
        
        function filterChannels() {
            const searchTerm = document.getElementById('search-input').value.toLowerCase();
            const categoryFilter = document.getElementById('category-filter').value;
            
            let filtered = allChannels.filter(channel => {
                const matchesSearch = channel.channel_name.toLowerCase().includes(searchTerm);
                const matchesCategory = !categoryFilter || channel.category === categoryFilter;
                return matchesSearch && matchesCategory;
            });
            
            renderChannels(filtered);
        }
        
        function sortChannels() {
            const sortBy = document.getElementById('sort-select').value;
            const container = document.getElementById('channels-container');
            const cards = Array.from(container.querySelectorAll('.channel-card'));
            
            cards.sort((a, b) => {
                switch(sortBy) {
                    case 'subs-desc':
                        return parseInt(b.dataset.subs) - parseInt(a.dataset.subs);
                    case 'subs-asc':
                        return parseInt(a.dataset.subs) - parseInt(b.dataset.subs);
                    case 'name-asc':
                        return a.dataset.name.localeCompare(b.dataset.name);
                    case 'name-desc':
                        return b.dataset.name.localeCompare(a.dataset.name);
                    default:
                        return 0;
                }
            });
            
            container.innerHTML = '';
            cards.forEach(card => container.appendChild(card));
        }
        
        function resetFilters() {
            document.getElementById('search-input').value = '';
            document.getElementById('category-filter').value = '';
            document.getElementById('sort-select').value = 'subs-desc';
            filterChannels();
            sortChannels();
        }
        
        // Initialize
        renderChannels(allChannels);
    </script>
</body>
</html>'''


def generate_channels_html(channels: List[Dict], contacts_map: Dict) -> str:
    """Generate HTML for channel cards"""
    html_parts = []
    
    for channel in channels:
        channel_id = channel['channel_id']
        contacts = contacts_map.get(channel_id, [])
        
        # Format contacts
        contact_items = []
        for contact in contacts:
            contact_type = contact['contact_type']
            contact_value = contact['contact_value']
            
            if contact_type == 'email':
                contact_items.append(f'<a href="mailto:{contact_value}" target="_blank" class="contact-item"><span class="contact-icon">📧</span> {contact_value}</a>')
            elif contact_type == 'instagram':
                contact_items.append(f'<a href="https://instagram.com/{contact_value}" target="_blank" class="contact-item"><span class="contact-icon">📸</span> @{contact_value}</a>')
            elif contact_type == 'twitter':
                contact_items.append(f'<a href="https://twitter.com/{contact_value}" target="_blank" class="contact-item"><span class="contact-icon">🐦</span> @{contact_value}</a>')
            elif contact_type == 'facebook':
                contact_items.append(f'<a href="https://facebook.com/{contact_value}" target="_blank" class="contact-item"><span class="contact-icon">📘</span> {contact_value}</a>')
            else:
                contact_items.append(f'<a href="https://{contact_value}" target="_blank" class="contact-item"><span class="contact-icon">🌐</span> {contact_value}</a>')
        
        contacts_html = ''.join(contact_items) if contact_items else '<div class="no-contacts">No contact info yet - visit About page</div>'
        
        subs = channel['subscriber_count'] or 0
        subs_formatted = f"{subs:,}" if subs < 1000 else (f"{subs/1000:.1f}K" if subs < 1000000 else f"{subs/1000000:.1f}M")
        
        about_url = f"{channel['channel_url']}/about"
        
        html = f'''
        <div class="channel-card" data-category="{channel['category']}" data-name="{channel['channel_name']}" data-subs="{subs}">
            <div class="channel-header">
                <div class="channel-name">
                    <a href="{channel['channel_url']}" target="_blank">{channel['channel_name']}</a>
                    <a href="{about_url}" target="_blank" class="channel-about-link">About Page</a>
                </div>
                <div class="subscriber-count">
                    👥 {subs_formatted} subscribers
                </div>
                <span class="category-badge category-{channel['category']}">{channel['category']}</span>
            </div>
            <div class="contacts">
                {contacts_html}
            </div>
        </div>
        '''
        html_parts.append(html)
    
    return ''.join(html_parts)


def main():
    """Generate interactive HTML viewer"""
    print("🌐 Generating Interactive Channel Viewer")
    print("=" * 50)
    
    # Connect to database
    db = ChannelDatabase()
    db.connect()
    
    # Get all channels
    channels = db.get_all_channels()
    print(f"✓ Loaded {len(channels)} channels")
    
    # Get contacts for each channel
    contacts_map = {}
    for channel in channels:
        contacts = db.get_contacts(channel['channel_id'])
        contacts_map[channel['channel_id']] = contacts
        
        # Add contacts to channel object for JSON
        channel['contacts'] = contacts
    
    # Get stats
    stats = db.get_stats()
    
    # Generate HTML
    channels_html = generate_channels_html(channels, contacts_map)
    channels_json = json.dumps(channels, default=str)
    
    html = HTML_TEMPLATE.replace('{{total_channels}}', str(stats['total_channels']))
    html = html.replace('{{channels_with_email}}', str(stats['channels_with_email']))
    html = html.replace('{{target_range}}', str(stats['target_range_channels']))
    html = html.replace('{{channels_html}}', channels_html)
    html = html.replace('{{channels_json}}', channels_json)
    
    # Save HTML file
    output_file = 'channels_viewer.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✓ Generated {output_file}")
    print(f"\n📊 Stats:")
    for key, value in stats.items():
        print(f"  {key.replace('_', ' ').title()}: {value}")
    
    db.close()
    
    print(f"\n✅ Open {output_file} in your browser to view all channels!")
    print("   Features:")
    print("   - 🔍 Search by name")
    print("   - 🏷️ Filter by category")
    print("   - 📊 Sort by subscribers or name")
    print("   - 🔗 Direct links to channels & About pages")
    print("   - 📧 Clickable contact info")


if __name__ == "__main__":
    main()

