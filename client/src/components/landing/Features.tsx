import { motion } from 'framer-motion';
import { MessageSquare, User, Zap, GitBranch } from 'lucide-react';

export default function Features() {
  const features = [
    {
      icon: <MessageSquare size={24} />,
      title: "Objection Classification",
      description: "Automatically detects price, trust, timing, competitor, and fit objections — and routes each to the right playbook."
    },
    {
      icon: <User size={24} />,
      title: "Buyer Persona Detection",
      description: "Identifies the prospect's role and communication style so every response feels like it was written for them specifically."
    },
    {
      icon: <Zap size={24} />,
      title: "Real-Time Response",
      description: "Responses generated in under 2 seconds. No waiting, no lag, no dropped momentum in the conversation."
    },
    {
      icon: <GitBranch size={24} />,
      title: "Smart Handoff",
      description: "When confidence drops or frustration spikes, Auralis flags the conversation for a human — before the deal is at risk."
    }
  ];

  return (
    <section id="features" className="w-full bg-[#0a0a0a] py-28 px-6">
      <div className="max-w-6xl mx-auto">
        <div className="flex flex-col items-start mb-16">
          <span className="text-xs font-sans font-medium tracking-widest text-[#dd6668] uppercase mb-4">
            FEATURES
          </span>
          <h2 className="font-display text-4xl md:text-5xl text-white leading-tight max-w-xl">
            Everything your sales team needs, automated.
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              className="bg-[#111111] border border-[#1f1f1f] rounded-2xl p-8 hover:border-[#dd6668]/30 transition-colors duration-300"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-80px' }}
              transition={{ duration: 0.5, delay: index * 0.15 }}
            >
              <div className="w-12 h-12 rounded-lg bg-[#dd6668]/10 flex items-center justify-center text-[#dd6668] mb-6">
                {feature.icon}
              </div>
              <h3 className="text-white font-sans font-medium text-lg mb-3">
                {feature.title}
              </h3>
              <p className="text-[#6b7280] font-sans text-sm leading-relaxed">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
