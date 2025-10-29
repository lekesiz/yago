/**
 * YAGO v8.1 - Template Marketplace Component
 * Pre-built project templates for rapid development
 */
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';

interface Template {
  id: string;
  name: string;
  description: string;
  category: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  icon: string;
  tags: string[];
  estimated_duration: string;
  estimated_cost: number;
  tech_stack: string[];
  popular: boolean;
}

interface Category {
  id: string;
  name: string;
  icon: string;
  description: string;
}

const categories: Category[] = [
  { id: 'all', name: 'All Templates', icon: '🌟', description: 'Browse all available templates' },
  { id: 'web', name: 'Web Development', icon: '🌐', description: 'Full-stack web applications' },
  { id: 'backend', name: 'Backend & API', icon: '🔌', description: 'REST APIs and microservices' },
  { id: 'mobile', name: 'Mobile Apps', icon: '📱', description: 'iOS and Android applications' },
  { id: 'data', name: 'Data Science', icon: '📊', description: 'ML, AI, and data pipelines' },
  { id: 'devops', name: 'DevOps', icon: '🔧', description: 'CI/CD and infrastructure' }
];

const templateData: Template[] = [
  {
    id: 'fastapi-rest-api',
    name: 'Python FastAPI REST API',
    description: 'Production-ready REST API with FastAPI, PostgreSQL, authentication, and Docker',
    category: 'backend',
    difficulty: 'intermediate',
    icon: '⚡',
    tags: ['python', 'fastapi', 'postgresql', 'docker', 'jwt'],
    estimated_duration: '1-2 weeks',
    estimated_cost: 12.50,
    tech_stack: ['Python 3.11', 'FastAPI', 'PostgreSQL', 'Docker', 'JWT Auth'],
    popular: true
  },
  {
    id: 'react-dashboard',
    name: 'React Admin Dashboard',
    description: 'Modern admin dashboard with React, TypeScript, TailwindCSS, and charts',
    category: 'web',
    difficulty: 'intermediate',
    icon: '📊',
    tags: ['react', 'typescript', 'tailwind', 'charts', 'dashboard'],
    estimated_duration: '2-3 weeks',
    estimated_cost: 18.75,
    tech_stack: ['React 18', 'TypeScript', 'TailwindCSS', 'Recharts', 'Framer Motion'],
    popular: true
  },
  {
    id: 'nextjs-saas',
    name: 'Next.js SaaS Starter',
    description: 'Complete SaaS boilerplate with authentication, payments, and admin panel',
    category: 'web',
    difficulty: 'advanced',
    icon: '💼',
    tags: ['nextjs', 'stripe', 'prisma', 'auth', 'saas'],
    estimated_duration: '4-6 weeks',
    estimated_cost: 45.00,
    tech_stack: ['Next.js 14', 'Prisma', 'Stripe', 'NextAuth', 'Tailwind'],
    popular: true
  },
  {
    id: 'django-api',
    name: 'Django REST Framework API',
    description: 'Scalable REST API with Django, Redis caching, and comprehensive testing',
    category: 'backend',
    difficulty: 'intermediate',
    icon: '🐍',
    tags: ['python', 'django', 'redis', 'celery', 'api'],
    estimated_duration: '2-3 weeks',
    estimated_cost: 16.25,
    tech_stack: ['Django 5', 'DRF', 'PostgreSQL', 'Redis', 'Celery'],
    popular: false
  },
  {
    id: 'react-native-app',
    name: 'React Native Mobile App',
    description: 'Cross-platform mobile app with navigation, state management, and API integration',
    category: 'mobile',
    difficulty: 'advanced',
    icon: '📱',
    tags: ['react-native', 'expo', 'redux', 'navigation', 'mobile'],
    estimated_duration: '4-5 weeks',
    estimated_cost: 32.00,
    tech_stack: ['React Native', 'Expo', 'Redux Toolkit', 'React Navigation'],
    popular: true
  },
  {
    id: 'nodejs-express',
    name: 'Node.js Express API',
    description: 'RESTful API with Express, MongoDB, authentication, and rate limiting',
    category: 'backend',
    difficulty: 'beginner',
    icon: '🟢',
    tags: ['nodejs', 'express', 'mongodb', 'jwt', 'api'],
    estimated_duration: '1 week',
    estimated_cost: 8.50,
    tech_stack: ['Node.js 20', 'Express', 'MongoDB', 'JWT', 'Mongoose'],
    popular: true
  },
  {
    id: 'ml-pipeline',
    name: 'ML Data Pipeline',
    description: 'End-to-end ML pipeline with data ingestion, training, and deployment',
    category: 'data',
    difficulty: 'advanced',
    icon: '🤖',
    tags: ['python', 'sklearn', 'pandas', 'mlops', 'airflow'],
    estimated_duration: '3-4 weeks',
    estimated_cost: 28.00,
    tech_stack: ['Python', 'Scikit-learn', 'Pandas', 'MLflow', 'Apache Airflow'],
    popular: false
  },
  {
    id: 'vue-spa',
    name: 'Vue.js Single Page App',
    description: 'Modern SPA with Vue 3, Composition API, Pinia state management, and routing',
    category: 'web',
    difficulty: 'intermediate',
    icon: '💚',
    tags: ['vue', 'pinia', 'vite', 'spa', 'typescript'],
    estimated_duration: '2 weeks',
    estimated_cost: 14.00,
    tech_stack: ['Vue 3', 'Pinia', 'Vue Router', 'Vite', 'TypeScript'],
    popular: false
  },
  {
    id: 'kubernetes-cluster',
    name: 'Kubernetes Cluster Setup',
    description: 'Production-ready K8s cluster with monitoring, logging, and auto-scaling',
    category: 'devops',
    difficulty: 'advanced',
    icon: '☸️',
    tags: ['kubernetes', 'helm', 'prometheus', 'grafana', 'devops'],
    estimated_duration: '2-3 weeks',
    estimated_cost: 22.50,
    tech_stack: ['Kubernetes', 'Helm', 'Prometheus', 'Grafana', 'Istio'],
    popular: false
  },
  {
    id: 'flutter-app',
    name: 'Flutter Mobile App',
    description: 'Beautiful cross-platform mobile app with Material Design and state management',
    category: 'mobile',
    difficulty: 'intermediate',
    icon: '🦋',
    tags: ['flutter', 'dart', 'firebase', 'bloc', 'mobile'],
    estimated_duration: '3-4 weeks',
    estimated_cost: 24.00,
    tech_stack: ['Flutter', 'Dart', 'Firebase', 'BLoC Pattern', 'Material Design'],
    popular: false
  },
  {
    id: 'graphql-api',
    name: 'GraphQL API Server',
    description: 'Modern GraphQL API with Apollo Server, PostgreSQL, and subscriptions',
    category: 'backend',
    difficulty: 'advanced',
    icon: '🔷',
    tags: ['graphql', 'apollo', 'nodejs', 'postgresql', 'subscriptions'],
    estimated_duration: '2-3 weeks',
    estimated_cost: 19.00,
    tech_stack: ['GraphQL', 'Apollo Server', 'Node.js', 'PostgreSQL', 'Redis'],
    popular: false
  },
  {
    id: 'data-dashboard',
    name: 'Analytics Dashboard',
    description: 'Interactive data visualization dashboard with real-time updates and exports',
    category: 'data',
    difficulty: 'intermediate',
    icon: '📈',
    tags: ['python', 'streamlit', 'plotly', 'pandas', 'dashboard'],
    estimated_duration: '1-2 weeks',
    estimated_cost: 11.00,
    tech_stack: ['Python', 'Streamlit', 'Plotly', 'Pandas', 'PostgreSQL'],
    popular: true
  }
];

const difficultyColors = {
  beginner: 'from-green-500 to-emerald-500',
  intermediate: 'from-yellow-500 to-orange-500',
  advanced: 'from-red-500 to-pink-500'
};

const difficultyIcons = {
  beginner: '🌱',
  intermediate: '🔥',
  advanced: '💎'
};

export const MarketplaceTab: React.FC = () => {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [filteredTemplates, setFilteredTemplates] = useState<Template[]>([]);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('all');
  const [showPopularOnly, setShowPopularOnly] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load templates
    setTemplates(templateData);
    setFilteredTemplates(templateData);
    setLoading(false);
  }, []);

  useEffect(() => {
    // Apply filters
    let filtered = templates;

    // Category filter
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(t => t.category === selectedCategory);
    }

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(t =>
        t.name.toLowerCase().includes(query) ||
        t.description.toLowerCase().includes(query) ||
        t.tags.some(tag => tag.toLowerCase().includes(query))
      );
    }

    // Difficulty filter
    if (selectedDifficulty !== 'all') {
      filtered = filtered.filter(t => t.difficulty === selectedDifficulty);
    }

    // Popular filter
    if (showPopularOnly) {
      filtered = filtered.filter(t => t.popular);
    }

    setFilteredTemplates(filtered);
  }, [selectedCategory, searchQuery, selectedDifficulty, showPopularOnly, templates]);

  const handleUseTemplate = (template: Template) => {
    toast.success(`Template "${template.name}" selected! This would pre-fill the project creation form.`, {
      duration: 3000,
      icon: '🚀'
    });
    // In a real implementation, this would navigate to create project tab with pre-filled data
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full"
        />
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-8">
      {/* Header */}
      <div>
        <h2 className="text-4xl font-bold bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400 bg-clip-text text-transparent mb-2">
          Template Marketplace
        </h2>
        <p className="text-gray-400">
          Pre-built project templates to accelerate your development
        </p>
      </div>

      {/* Search and Filters */}
      <div className="space-y-4">
        {/* Search Bar */}
        <div className="relative">
          <input
            type="text"
            placeholder="Search templates by name, description, or tags..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl px-6 py-4 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
          />
          <div className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 text-xl">
            🔍
          </div>
        </div>

        {/* Filters Row */}
        <div className="flex flex-wrap items-center gap-4">
          {/* Difficulty Filter */}
          <div className="flex gap-2 bg-white/5 backdrop-blur-sm rounded-lg p-1 border border-white/10">
            <button
              onClick={() => setSelectedDifficulty('all')}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all ${
                selectedDifficulty === 'all'
                  ? 'bg-white/20 text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              All Levels
            </button>
            {['beginner', 'intermediate', 'advanced'].map(level => (
              <button
                key={level}
                onClick={() => setSelectedDifficulty(level)}
                className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all flex items-center gap-1 ${
                  selectedDifficulty === level
                    ? 'bg-white/20 text-white'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                <span>{difficultyIcons[level as keyof typeof difficultyIcons]}</span>
                <span className="capitalize">{level}</span>
              </button>
            ))}
          </div>

          {/* Popular Toggle */}
          <button
            onClick={() => setShowPopularOnly(!showPopularOnly)}
            className={`px-4 py-2 rounded-lg font-medium transition-all flex items-center gap-2 ${
              showPopularOnly
                ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white'
                : 'bg-white/5 text-gray-400 hover:text-white border border-white/10'
            }`}
          >
            <span>⭐</span>
            <span>Popular Only</span>
          </button>

          {/* Results Count */}
          <div className="ml-auto text-gray-400 text-sm">
            {filteredTemplates.length} template{filteredTemplates.length !== 1 ? 's' : ''} found
          </div>
        </div>
      </div>

      {/* Category Tabs */}
      <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-hide">
        {categories.map(category => (
          <motion.button
            key={category.id}
            onClick={() => setSelectedCategory(category.id)}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className={`flex-shrink-0 px-6 py-3 rounded-xl font-medium transition-all ${
              selectedCategory === category.id
                ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg'
                : 'bg-white/5 text-gray-400 hover:text-white hover:bg-white/10 border border-white/10'
            }`}
          >
            <div className="flex items-center gap-2">
              <span className="text-xl">{category.icon}</span>
              <span>{category.name}</span>
            </div>
          </motion.button>
        ))}
      </div>

      {/* Templates Grid */}
      <AnimatePresence mode="popLayout">
        {filteredTemplates.length === 0 ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="text-center py-16"
          >
            <div className="text-6xl mb-4">🔍</div>
            <h3 className="text-2xl font-bold text-white mb-2">No templates found</h3>
            <p className="text-gray-400">Try adjusting your filters or search query</p>
          </motion.div>
        ) : (
          <motion.div
            layout
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
          >
            {filteredTemplates.map((template, idx) => (
              <motion.div
                key={template.id}
                layout
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ delay: idx * 0.05 }}
                className="group relative bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 hover:border-purple-500/50 transition-all overflow-hidden"
              >
                {/* Popular Badge */}
                {template.popular && (
                  <div className="absolute top-4 right-4 z-10 bg-gradient-to-r from-yellow-500 to-orange-500 text-white text-xs font-bold px-3 py-1 rounded-full flex items-center gap-1">
                    <span>⭐</span>
                    <span>Popular</span>
                  </div>
                )}

                {/* Card Content */}
                <div className="p-6">
                  {/* Icon and Difficulty */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="text-5xl">{template.icon}</div>
                    <div className={`bg-gradient-to-r ${difficultyColors[template.difficulty]} text-white text-xs font-bold px-3 py-1 rounded-full flex items-center gap-1`}>
                      <span>{difficultyIcons[template.difficulty]}</span>
                      <span className="capitalize">{template.difficulty}</span>
                    </div>
                  </div>

                  {/* Template Name */}
                  <h3 className="text-xl font-bold text-white mb-2 group-hover:text-purple-400 transition-colors">
                    {template.name}
                  </h3>

                  {/* Description */}
                  <p className="text-gray-400 text-sm mb-4 line-clamp-2">
                    {template.description}
                  </p>

                  {/* Tech Stack */}
                  <div className="mb-4">
                    <div className="text-xs text-gray-500 mb-2">Tech Stack:</div>
                    <div className="flex flex-wrap gap-1">
                      {template.tech_stack.slice(0, 3).map(tech => (
                        <span
                          key={tech}
                          className="bg-white/10 text-gray-300 text-xs px-2 py-1 rounded-md"
                        >
                          {tech}
                        </span>
                      ))}
                      {template.tech_stack.length > 3 && (
                        <span className="bg-white/10 text-gray-300 text-xs px-2 py-1 rounded-md">
                          +{template.tech_stack.length - 3} more
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Tags */}
                  <div className="flex flex-wrap gap-1 mb-4">
                    {template.tags.slice(0, 4).map(tag => (
                      <span
                        key={tag}
                        className="bg-purple-500/20 text-purple-300 text-xs px-2 py-1 rounded-full"
                      >
                        #{tag}
                      </span>
                    ))}
                  </div>

                  {/* Stats */}
                  <div className="grid grid-cols-2 gap-3 mb-4 text-sm">
                    <div className="bg-black/20 rounded-lg p-2">
                      <div className="text-gray-500 text-xs">Duration</div>
                      <div className="text-white font-medium">{template.estimated_duration}</div>
                    </div>
                    <div className="bg-black/20 rounded-lg p-2">
                      <div className="text-gray-500 text-xs">Est. Cost</div>
                      <div className="text-green-400 font-bold">${template.estimated_cost}</div>
                    </div>
                  </div>

                  {/* Use Template Button */}
                  <button
                    onClick={() => handleUseTemplate(template)}
                    className="w-full bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-bold py-3 rounded-xl transition-all transform hover:scale-105 flex items-center justify-center gap-2"
                  >
                    <span>🚀</span>
                    <span>Use Template</span>
                  </button>
                </div>

                {/* Hover Effect */}
                <div className="absolute inset-0 bg-gradient-to-t from-purple-500/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
              </motion.div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Statistics Footer */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="bg-gradient-to-r from-purple-500/10 via-pink-500/10 to-cyan-500/10 backdrop-blur-sm rounded-2xl p-8 border border-white/10"
      >
        <h3 className="text-2xl font-bold text-white mb-6 text-center">
          Why Use Templates?
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[
            { icon: '⚡', title: 'Save Time', description: 'Launch projects 10x faster with pre-built code' },
            { icon: '🎯', title: 'Best Practices', description: 'Follow industry standards and patterns' },
            { icon: '💰', title: 'Cost Effective', description: 'Reduce development costs significantly' },
            { icon: '🔧', title: 'Customizable', description: 'Fully customizable to your needs' }
          ].map((feature, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 + idx * 0.1 }}
              className="text-center"
            >
              <div className="text-4xl mb-3">{feature.icon}</div>
              <h4 className="text-white font-bold mb-2">{feature.title}</h4>
              <p className="text-gray-400 text-sm">{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  );
};
