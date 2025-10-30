/**
 * YAGO v8.0 - Marketplace Tab Component
 */
import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';

interface MarketplaceItem {
  id: string;
  name: string;
  type: string;
  description: string;
  author: string;
  version: string;
  downloads: number;
  rating: number;
  price: string;
  icon: string;
  tags: string[];
  installed: boolean;
}

export const MarketplaceTab: React.FC = () => {
  const [items, setItems] = useState<MarketplaceItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');

  useEffect(() => {
    loadItems();
  }, [filter]);

  const loadItems = () => {
    const url = filter === 'all' 
      ? 'http://localhost:8000/api/v1/marketplace/items'
      : `http://localhost:8000/api/v1/marketplace/items?item_type=${filter}`;

    fetch(url)
      .then(r => r.json())
      .then(data => setItems(data.items || []))
      .catch(() => toast.error('Failed to load marketplace'))
      .finally(() => setLoading(false));
  };

  const installItem = async (itemId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/marketplace/items/${itemId}/install`, {
        method: 'POST'
      });
      const data = await response.json();
      toast.success(data.message);
      loadItems();
    } catch {
      toast.error('Installation failed');
    }
  };

  if (loading) return <div className="text-white text-center py-8">Loading marketplace...</div>;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-white mb-2">Marketplace</h2>
        <p className="text-gray-400">{items.length} plugins, templates & integrations</p>
      </div>

      {/* Type Filter */}
      <div className="flex space-x-2">
        {['all', 'plugin', 'template', 'integration'].map((type) => (
          <button
            key={type}
            onClick={() => setFilter(type)}
            className={`px-4 py-2 rounded-lg font-medium transition ${
              filter === type ? 'bg-purple-600 text-white' : 'bg-white/10 text-gray-300 hover:bg-white/20'
            }`}
          >
            {type.charAt(0).toUpperCase() + type.slice(1)}
          </button>
        ))}
      </div>

      {/* Items Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {items.map((item) => (
          <div key={item.id} className="bg-white/5 backdrop-blur-sm rounded-lg p-6 border border-white/10 hover:border-purple-500 transition">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className="text-4xl">{item.icon}</div>
                <div>
                  <h3 className="font-bold text-white">{item.name}</h3>
                  <p className="text-xs text-gray-400 capitalize">{item.type}</p>
                </div>
              </div>
            </div>

            <p className="text-sm text-gray-400 mb-4">{item.description}</p>

            <div className="flex items-center space-x-4 mb-4 text-xs text-gray-400">
              <span>⭐ {item.rating}</span>
              <span>⬇️ {item.downloads.toLocaleString()}</span>
              <span className="text-purple-400">{item.price}</span>
            </div>

            <div className="flex flex-wrap gap-1 mb-4">
              {item.tags.slice(0, 3).map((tag) => (
                <span key={tag} className="text-xs px-2 py-1 rounded bg-purple-500/20 text-purple-300">
                  {tag}
                </span>
              ))}
            </div>

            <div className="text-xs text-gray-500 mb-3">v{item.version} by {item.author}</div>

            <button
              onClick={() => installItem(item.id)}
              className="w-full px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white font-medium rounded-lg transition"
            >
              {item.installed ? 'Installed ✓' : 'Install'}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};
