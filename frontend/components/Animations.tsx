// frontend/components/Animations.tsx
import React from 'react'

export const FadeIn = ({ children, delay = 0 }: { children: React.ReactNode, delay?: number }) => (
  <div
    className="animate-fade-in"
    style={{ animationDelay: `${delay}ms` }}
  >
    {children}
  </div>
);

export const SlideUp = ({ children }: { children: React.ReactNode }) => (
  <div className="animate-slide-up">
    {children}
  </div>
);