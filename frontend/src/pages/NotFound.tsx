/**
 * 404 Not Found Page
 * Broken patch cable visualization
 */
import { Link } from 'react-router-dom';
import './NotFound.css';

export default function NotFound() {
  return (
    <div className="not-found-container">
      <div className="not-found-content">
        {/* 404 Broken Patch Cable SVG */}
        <svg
          width="400"
          height="400"
          viewBox="0 0 400 400"
          xmlns="http://www.w3.org/2000/svg"
          className="broken-patch"
        >
          <defs>
            <filter id="error-glow">
              <feGaussianBlur stdDeviation="4" result="coloredBlur" />
              <feMerge>
                <feMergeNode in="coloredBlur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>

            <linearGradient id="cable-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#7FF7FF" />
              <stop offset="50%" stopColor="#FF1EA0" />
              <stop offset="100%" stopColor="#7FF7FF" />
            </linearGradient>
          </defs>

          {/* Broken hex frame */}
          <path
            d="M 200,40 L 330,110 L 330,180"
            fill="none"
            stroke="#FF1EA0"
            strokeWidth="3"
            filter="url(#error-glow)"
          />
          <path
            d="M 330,220 L 330,250 L 200,320 L 70,250 L 70,110 L 130,75"
            fill="none"
            stroke="#FF1EA0"
            strokeWidth="3"
            filter="url(#error-glow)"
          />

          {/* Break/crack visual */}
          <path
            d="M 330,180 L 340,185 L 335,195 L 330,220"
            fill="none"
            stroke="#FF1EA0"
            strokeWidth="2"
            strokeDasharray="3,3"
            opacity="0.6"
          />

          {/* Disconnected patch cable (left side) */}
          <path
            d="M 100,150 Q 120,170 150,180 T 180,190"
            fill="none"
            stroke="url(#cable-gradient)"
            strokeWidth="4"
            strokeLinecap="round"
            className="cable-left"
          />

          {/* Cable jack (left) */}
          <circle cx="100" cy="150" r="8" fill="#7FF7FF" filter="url(#error-glow)" />
          <circle cx="100" cy="150" r="4" fill="#020407" />

          {/* Disconnected patch cable (right side) */}
          <path
            d="M 300,150 Q 280,170 250,180 T 220,190"
            fill="none"
            stroke="url(#cable-gradient)"
            strokeWidth="4"
            strokeLinecap="round"
            className="cable-right"
          />

          {/* Cable jack (right) */}
          <circle cx="300" cy="150" r="8" fill="#7FF7FF" filter="url(#error-glow)" />
          <circle cx="300" cy="150" r="4" fill="#020407" />

          {/* Error sparks */}
          <circle cx="185" cy="188" r="3" fill="#FF1EA0" className="spark spark-1" />
          <circle cx="190" cy="195" r="2" fill="#FF1EA0" className="spark spark-2" />
          <circle cx="210" cy="192" r="2.5" fill="#FF1EA0" className="spark spark-3" />
          <circle cx="215" cy="188" r="3" fill="#FF1EA0" className="spark spark-4" />

          {/* 404 text integrated into design */}
          <text
            x="200"
            y="280"
            fill="#FF1EA0"
            fontFamily="JetBrains Mono, monospace"
            fontSize="72"
            fontWeight="bold"
            textAnchor="middle"
            filter="url(#error-glow)"
          >
            404
          </text>
        </svg>

        {/* Error message */}
        <h1 className="error-title">SIGNAL NOT FOUND</h1>
        <p className="error-description">
          The patch you're looking for has been disconnected or never existed.
        </p>

        {/* Navigation */}
        <div className="error-actions">
          <Link to="/" className="btn-primary">
            Return to Home
          </Link>
          <Link to="/modules" className="btn-secondary">
            Browse Modules
          </Link>
        </div>

        {/* Technical details */}
        <div className="error-details">
          <code>ERROR_CODE: PATCH_DISCONNECTED</code>
          <code>STATUS: 404 NOT_FOUND</code>
          <code>SUGGESTED_ACTION: RECONNECT_OR_RETURN_HOME</code>
        </div>
      </div>
    </div>
  );
}
