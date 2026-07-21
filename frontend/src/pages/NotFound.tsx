/**
 * 404 Not Found — Cyber Hive broken patch cable
 */
import { Link } from 'react-router-dom';
import './NotFound.css';

export default function NotFound() {
  return (
    <div className="not-found-container">
      <div className="not-found-content">
        <svg
          width="360"
          height="360"
          viewBox="0 0 400 400"
          xmlns="http://www.w3.org/2000/svg"
          className="broken-patch"
          aria-hidden="true"
        >
          <defs>
            <filter id="error-glow">
              <feGaussianBlur stdDeviation="3" result="coloredBlur" />
              <feMerge>
                <feMergeNode in="coloredBlur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
            <linearGradient id="cable-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#f5a623" />
              <stop offset="50%" stopColor="#3ddcff" />
              <stop offset="100%" stopColor="#f5a623" />
            </linearGradient>
          </defs>

          <path
            d="M 200,40 L 330,110 L 330,180"
            fill="none"
            stroke="#e23d4a"
            strokeWidth="3"
            filter="url(#error-glow)"
          />
          <path
            d="M 330,220 L 330,250 L 200,320 L 70,250 L 70,110 L 130,75"
            fill="none"
            stroke="#e23d4a"
            strokeWidth="3"
            filter="url(#error-glow)"
          />
          <path
            d="M 330,180 L 340,185 L 335,195 L 330,220"
            fill="none"
            stroke="#e23d4a"
            strokeWidth="2"
            strokeDasharray="3,3"
            opacity="0.6"
          />

          <path
            d="M 100,150 Q 120,170 150,180 T 180,190"
            fill="none"
            stroke="url(#cable-gradient)"
            strokeWidth="4"
            strokeLinecap="round"
            className="cable-left"
          />
          <circle cx="100" cy="150" r="8" fill="#f5a623" filter="url(#error-glow)" />
          <circle cx="100" cy="150" r="4" fill="#08090b" />

          <path
            d="M 300,150 Q 280,170 250,180 T 220,190"
            fill="none"
            stroke="url(#cable-gradient)"
            strokeWidth="4"
            strokeLinecap="round"
            className="cable-right"
          />
          <circle cx="300" cy="150" r="8" fill="#3ddcff" filter="url(#error-glow)" />
          <circle cx="300" cy="150" r="4" fill="#08090b" />

          <circle cx="185" cy="188" r="3" fill="#e23d4a" className="spark spark-1" />
          <circle cx="190" cy="195" r="2" fill="#ff8a3d" className="spark spark-2" />
          <circle cx="210" cy="192" r="2.5" fill="#e23d4a" className="spark spark-3" />
          <circle cx="215" cy="188" r="3" fill="#ff8a3d" className="spark spark-4" />

          <text
            x="200"
            y="280"
            fill="#f5a623"
            fontFamily="ui-monospace, monospace"
            fontSize="72"
            fontWeight="bold"
            textAnchor="middle"
            filter="url(#error-glow)"
          >
            404
          </text>
        </svg>

        <p className="eyebrow">Signal loss</p>
        <h1 className="error-title">Patch not found</h1>
        <p className="error-description">
          The route you requested has been disconnected or never existed in this hive.
        </p>

        <div className="error-actions">
          <Link to="/" className="button button-primary">
            Return home
          </Link>
          <Link to="/modules" className="button button-secondary">
            Browse modules
          </Link>
          <Link to="/racks" className="button button-quiet">
            Open rigs
          </Link>
        </div>

        <div className="error-details">
          <code>ERROR_CODE: PATCH_DISCONNECTED</code>
          <code>STATUS: 404 NOT_FOUND</code>
          <code>SUGGESTED_ACTION: RECONNECT_OR_RETURN_HOME</code>
        </div>
      </div>
    </div>
  );
}
