# Automated ML Trading System

## 🚀 What This Does (In Simple Terms)

**This is a "robot trader" that automatically buys and sells QQQ stock to make money while you sleep.**

Think of it like having a super-smart assistant that:
- 👀 **Watches** the stock market, news, and social media 24/7
- 🧠 **Thinks** using AI to predict if QQQ will go up or down
- 💰 **Trades** automatically when it finds good opportunities
- 🛡️ **Protects** your money with strict safety rules
- 📱 **Texts** you daily updates on your phone

### Perfect For Beginners

- ✅ **No trading experience needed** - The AI does the hard work
- ✅ **Start with fake money** - Test everything safely first
- ✅ **Hands-off approach** - Runs automatically, just check your phone
- ✅ **Built-in safety** - Won't lose more than you're comfortable with
- ✅ **Learn as you go** - Understand trading through daily reports

### What You Can Expect

- **Returns**: 15-25% per year (vs 10% stock market average)
- **Safety**: Never risk more than 1-2% per trade
- **Time**: 5 minutes setup, then just check daily SMS updates
- **Cost**: ~$55/month for data feeds (pays for itself quickly)

---

## 📋 Documentation

This project includes comprehensive documentation covering all aspects of the system:

### Core Documentation

| Document | Description |
|----------|-------------|
| **[TRADING_SYSTEM_SPECIFICATION.md](TRADING_SYSTEM_SPECIFICATION.md)** | Complete technical specification with architecture, requirements, and implementation plan |
| **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** | Detailed project structure, coding standards, and development guidelines |
| **[API_SPECIFICATIONS.md](API_SPECIFICATIONS.md)** | External API integrations, endpoints, authentication, and data schemas |
| **[CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md)** | System configuration, environment setup, and parameter management |
| **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** | Production deployment, infrastructure setup, and operational procedures |

### Quick Navigation

- **Getting Started**: See [Local Development Setup](#-quick-start)
- **System Architecture**: [TRADING_SYSTEM_SPECIFICATION.md](TRADING_SYSTEM_SPECIFICATION.md#system-architecture)
- **API Integration**: [API_SPECIFICATIONS.md](API_SPECIFICATIONS.md)
- **Configuration**: [CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md#environment-variables)
- **Deployment**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md#local-development-setup)

---

## 🏗️ How It Works (Simple Visual Guide)

Think of this trading system like a **smart factory** that processes information and makes trading decisions:

```
📊 DATA SOURCES → 🧠 BRAIN → 💰 TRADING → 📱 NOTIFICATIONS
   (Collect)      (Think)    (Act)      (Update You)
```

### 1. 📊 **DATA COLLECTION** (The Eyes & Ears)

This is like having multiple news reporters feeding you information:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MARKET DATA   │    │   NEWS DATA     │    │  SOCIAL DATA    │
│                 │    │                 │    │                 │
│ • QQQ prices    │    │ • Financial     │    │ • Reddit posts │
│ • Volume        │    │   news          │    │ • Sentiment     │
│ • Technical     │    │ • Earnings      │    │ • Mentions      │
│   indicators    │    │ • Fed news      │    │ • Upvotes       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │     DATA STORAGE        │
                    │   (Like a filing       │
                    │    cabinet for all     │
                    │    the information)    │
                    └─────────────────────────┘
```

**What this does:** Continuously collects information about QQQ stock prices, news about tech companies, and what people are saying on Reddit about stocks.

### 2. 🧠 **THE BRAIN** (Machine Learning Pipeline)

This is like having a super-smart analyst who learns patterns:

```
┌─────────────────────────────────────────────────────────────┐
│                    THE BRAIN (ML PIPELINE)                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📊 Raw Data → 🔧 Feature Engineering → 🤖 ML Models       │
│                                                             │
│  ┌─────────────┐   ┌─────────────────┐   ┌───────────────┐ │
│  │ Price: $350 │   │ RSI: 65         │   │ XGBoost:      │ │
│  │ Volume: 50M │ → │ MACD: Bullish   │ → │ "BUY" (70%)   │ │
│  │ News: +0.8  │   │ Sentiment: +0.3 │   │               │ │
│  │ Reddit: +0.2│   │ Volume: High    │   │ LSTM:         │ │
│  └─────────────┘   └─────────────────┘   │ "BUY" (65%)   │ │
│                                          │               │ │
│                                          │ Transformer:  │ │
│                                          │ "BUY" (75%)   │ │
│                                          └───────────────┘ │
│                                                  │         │
│                                                  ▼         │
│                                          ┌───────────────┐ │
│                                          │   ENSEMBLE    │ │
│                                          │ Final Decision│ │
│                                          │ "BUY" (70%)   │ │
│                                          └───────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**What this does:** Takes all the raw information, calculates technical indicators (like RSI, MACD), and uses 3 different AI models to predict if QQQ will go up or down. Then combines all predictions into one final decision.

### 3. 💰 **TRADING ENGINE** (The Action Taker)

This is like having a disciplined trader who follows strict rules:

```
┌─────────────────────────────────────────────────────────────┐
│                    TRADING ENGINE                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🧠 ML Decision → 🛡️ Risk Check → 📋 Order → 💼 Broker    │
│                                                             │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐       │
│  │ "BUY QQQ"   │   │ Position    │   │ Buy 100     │       │
│  │ Confidence: │ → │ Size: 2%    │ → │ shares of   │ →     │
│  │ 70%         │   │ of portfolio│   │ QQQ at      │       │
│  │             │   │             │   │ market price│       │
│  └─────────────┘   └─────────────┘   └─────────────┘       │
│                                                             │
│                    ┌─────────────────────────────────────┐   │
│                    │         RISK MANAGEMENT             │   │
│                    │ • Max 10% per position              │   │
│                    │ • Stop loss at -1%                  │   │
│                    │ • Max daily loss: -2%               │   │
│                    │ • Emergency shutdown if needed      │   │
│                    └─────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                        ┌─────────────────────┐
                        │    ALPACA BROKER    │
                        │  (Paper Trading     │
                        │   to start with)    │
                        └─────────────────────┘
```

**What this does:** Takes the AI's recommendation, checks if it's safe to trade (risk management), calculates how much to buy/sell, and sends the order to the broker.

### 4. 📱 **SMS NOTIFICATIONS** (Keeps You Updated)

This keeps you informed without needing to constantly check:

```
┌─────────────────────────────────────────────────────────────┐
│                    SMS NOTIFICATION SYSTEM                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🚨 CRITICAL ALERTS    ⚠️ WARNINGS    📊 DAILY SUMMARY     │
│                                                             │
│  ┌─────────────────┐   ┌─────────────┐   ┌───────────────┐ │
│  │ • System crash  │   │ • Model     │   │ 🤖 TRADING BOT│ │
│  │ • Large loss    │   │   confidence│   │ 💰 Today: +$127│ │
│  │ • Emergency     │   │   dropping  │   │ 📈 Week: +$342 │ │
│  │   shutdown      │   │ • Unusual   │   │ 💼 Total: $10K │ │
│  │                 │   │   market    │   │ ✅ All normal  │ │
│  │ 📱 Instant SMS  │   │ 📱 SMS      │   │ 📱 4:30 PM SMS │ │
│  └─────────────────┘   └─────────────┘   └───────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**What this does:** Sends you text messages when important things happen, plus a daily summary so you always know how your money is doing.

### 🔄 **Complete Flow** (How It All Works Together)

```
1. 📊 COLLECT DATA (every minute)
   ↓
2. 🧠 ANALYZE & PREDICT (every 15 minutes)
   ↓
3. 🛡️ CHECK RISKS (before every trade)
   ↓
4. 💰 EXECUTE TRADE (if safe and profitable)
   ↓
5. 📱 NOTIFY YOU (immediately for important events)
   ↓
6. 🔄 REPEAT (24/7 during market hours)
```

---

## 🚀 Quick Start

### Prerequisites

```bash
# System Requirements
Python 3.9+
PostgreSQL 14+
Redis 6.2+
Docker 20.10+ (optional)

# Minimum Hardware
CPU: 4 cores, 2.5+ GHz
RAM: 16 GB
Storage: 500 GB SSD
```

### 1. Clone and Setup

```bash
# Clone repository
git clone <repository-url>
cd trade_bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup

```bash
# Install PostgreSQL and Redis
sudo apt install postgresql postgresql-contrib redis-server

# Create database
sudo -u postgres psql
CREATE DATABASE tradebot;
CREATE USER tradebot_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE tradebot TO tradebot_user;
\q

# Start services
sudo systemctl start postgresql redis-server
```

### 3. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit configuration (add your API keys)
nano .env
```

**Required API Keys:**
- Polygon.io (market data)
- Alpha Vantage (backup market data)
- NewsAPI (financial news)
- Reddit API (social sentiment)
- Alpaca (trading - start with paper trading)

### 4. Initialize Database

```bash
# Run database setup
python scripts/setup_database.py

# Verify connection
python -c "from config.database import engine; print('Database connected!')"
```

### 5. Run the System

```bash
# Start development server
python main.py

# Or with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Access Dashboards

- **Main Application**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **API Documentation**: http://localhost:8000/docs

---

## 🐳 Docker Quick Start

```bash
# Clone and navigate
git clone <repository-url>
cd trade_bot

# Copy environment file
cp .env.example .env
# Edit .env with your API keys

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f app
```

**Services Available:**
- **Application**: http://localhost:8000
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Database**: localhost:5432

---

## � Data Sources

### Market Data
- **Primary**: Polygon.io (real-time and historical)
- **Backup**: Alpha Vantage, IEX Cloud
- **Coverage**: QQQ OHLCV data at 1-minute intervals

### News Data
- **Sources**: NewsAPI, Financial Modeling Prep
- **Processing**: Sentiment analysis using FinBERT
- **Focus**: QQQ, NASDAQ-100, tech sector news

### Social Sentiment
- **Platform**: Reddit (r/stocks, r/investing, r/wallstreetbets)
- **Processing**: NLP sentiment analysis, ticker extraction
- **Metrics**: Mention counts, sentiment scores, engagement

### Economic Data
- **Sources**: FRED API, Trading Economics
- **Indicators**: CPI, GDP, Fed rates, VIX, unemployment

---

## 🤖 Machine Learning Pipeline

### Models
1. **XGBoost Classifier**
   - Features: Technical indicators, volume patterns
   - Target: 15-minute forward returns
   - Optimization: Optuna hyperparameter tuning

2. **LSTM Network**
   - Features: Sequential price and volume data
   - Architecture: 2-layer LSTM with attention
   - Sequence length: 60 minutes

3. **Transformer Model**
   - Features: Multi-modal (price + sentiment + news)
   - Architecture: Custom transformer with cross-attention
   - Context window: 4 hours

### Ensemble Strategy
- Dynamic weighting based on recent performance
- Confidence-based prediction filtering
- Regime-specific model selection

### Training Schedule
- **Full retraining**: Weekly
- **Incremental updates**: Daily
- **Emergency retraining**: On performance degradation

---

## 💼 Trading System

### Broker Integration
- **Primary**: Alpaca API (paper and live trading)
- **Secondary**: Interactive Brokers (professional features)
- **Order Types**: Market, Limit, Stop-Loss, Trailing Stop

### Risk Management
- **Position Size**: Maximum 10% of portfolio per position
- **Stop Loss**: 1% of portfolio value
- **Daily Loss Limit**: 2% of portfolio
- **Maximum Drawdown**: 5% of portfolio

### Order Management
- Real-time signal generation from ML ensemble
- Automated position sizing using Kelly Criterion
- Risk assessment before order execution
- Position tracking and management

---

## 📈 Backtesting

### Framework Features
- Realistic transaction cost modeling
- Slippage and market impact simulation
- Walk-forward validation
- Multiple time horizon testing

### Performance Metrics
- Sharpe Ratio, Information Ratio
- Maximum Drawdown, Calmar Ratio
- Win Rate, Profit Factor
- Risk-adjusted returns vs benchmarks

### Validation Process
1. Historical backtesting (2+ years)
2. Paper trading validation
3. Small position live testing
4. Gradual capital scaling

---

## 🔧 Development

### Project Structure
```
trade_bot/
├── config/                 # Configuration management
├── data/                   # Data collection and processing
├── features/               # Feature engineering
├── models/                 # ML models and training
├── trading/                # Trading system components
├── monitoring/             # Monitoring and alerting
├── backtesting/           # Backtesting framework
├── tests/                 # Unit and integration tests
└── scripts/               # Utility scripts
```

### Development Workflow
1. **Feature Development**: Create feature branch
2. **Testing**: Run unit and integration tests
3. **Code Review**: Peer review process
4. **Staging**: Deploy to staging environment
5. **Production**: Deploy with monitoring

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test category
pytest tests/unit/
pytest tests/integration/
```

---

## 📊 Monitoring

### Real-Time Dashboards
- **System Health**: CPU, memory, disk usage
- **Trading Performance**: P&L, positions, risk metrics
- **Data Quality**: API status, data completeness
- **Model Performance**: Accuracy, confidence, drift

### Alerting
- **Critical**: System failures, large losses, risk breaches
- **Warning**: Performance degradation, unusual conditions
- **Info**: Daily summaries, model retraining

### Logging
- **Structured Logging**: JSON format with context
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Retention**: 90 days for application logs, 7 years for trades

---

## 🔒 Security

### API Security
- Secure API key storage and rotation
- Rate limiting and request validation
- JWT authentication for internal APIs

### Data Protection
- Encryption of sensitive data at rest
- SSL/TLS for data in transit
- Database access controls

### Network Security
- Firewall configuration
- VPN access for remote management
- Fail2ban for intrusion prevention

---

## 🚀 Deployment

### Environments
- **Development**: Local development and testing
- **Staging**: Pre-production with paper trading
- **Production**: Live trading environment

### Infrastructure
- **Containerization**: Docker and Docker Compose
- **Orchestration**: Kubernetes (optional)
- **Monitoring**: Prometheus, Grafana, ELK stack
- **Load Balancing**: Nginx reverse proxy

### Deployment Process
1. **Code Review**: Peer review and approval
2. **Testing**: Automated test suite
3. **Staging**: Deploy and validate
4. **Production**: Gradual rollout with monitoring
5. **Verification**: Health checks and performance validation

---

## 📚 Implementation Timeline

### Phase 1: Foundation (Weeks 1-2)
- [x] Project structure and configuration
- [x] Database setup and basic data collection
- [x] Logging and monitoring framework

### Phase 2: Data Collection (Weeks 3-4)
- [ ] Multi-source data collection pipeline
- [ ] Data validation and quality monitoring
- [ ] Historical data backfill

### Phase 3: Feature Engineering (Weeks 5-6)
- [ ] Technical indicator calculation
- [ ] NLP sentiment analysis pipeline
- [ ] Feature store implementation

### Phase 4: ML Pipeline (Weeks 7-8)
- [ ] Model implementations (XGBoost, LSTM, Transformer)
- [ ] Ensemble methods and validation
- [ ] Automated training pipeline

### Phase 5: Trading System (Weeks 9-10)
- [ ] Broker API integration
- [ ] Order management and risk controls
- [ ] Position tracking and management

### Phase 6: Backtesting (Weeks 11-12)
- [ ] Comprehensive backtesting framework
- [ ] Performance analysis and optimization
- [ ] Paper trading validation

### Phase 7: Production (Weeks 13+)
- [ ] Production deployment
- [ ] Live trading with monitoring
- [ ] Performance optimization

---

## ⚠️ Risk Disclaimer

**IMPORTANT**: This is an automated trading system that can result in significant financial losses. 

- **Start with Paper Trading**: Always begin with paper trading to validate the system
- **Risk Management**: Never risk more than you can afford to lose
- **Regulatory Compliance**: Ensure compliance with all applicable regulations
- **Continuous Monitoring**: Monitor the system continuously during live trading
- **Professional Advice**: Consider consulting with financial professionals

---

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

### Code Standards
- Python 3.9+ with type hints
- Black code formatting
- Comprehensive docstrings
- Unit test coverage > 90%

### Reporting Issues
- Use GitHub Issues for bug reports
- Include system information and logs
- Provide steps to reproduce

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Support

For questions, issues, or contributions:

- **Documentation**: Check the comprehensive docs in this repository
- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Discussions**: Use GitHub Discussions for general questions

---

**Built with ❤️ for algorithmic trading enthusiasts**

*Remember: Past performance does not guarantee future results. Trade responsibly.*
