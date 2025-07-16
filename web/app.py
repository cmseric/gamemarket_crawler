 # -*- coding: utf-8 -*-
"""
Flask Web应用主文件
"""

import os
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from flask_caching import Cache
from loguru import logger

from web.config import config
from web.utils.database import DatabaseManager, SteamDataQuery, CacheManager


def create_app(config_name=None):
    """应用工厂函数"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config.get(config_name, config['default']))
    
    # 初始化缓存
    cache = Cache(app)
    
    # 初始化数据库管理器
    db_manager = DatabaseManager(app.config)
    steam_query = SteamDataQuery(db_manager)
    cache_manager = CacheManager(db_manager)
    
    @app.teardown_appcontext
    def close_db(error):
        """关闭数据库连接"""
        db_manager.close_connections()
    
    @app.route('/')
    def index():
        """首页 - 数据概览"""
        try:
            # 尝试从缓存获取数据
            cache_key = 'dashboard_summary'
            summary = cache_manager.get_cached_data(cache_key)
            
            if not summary:
                summary = steam_query.get_statistics_summary()
                # 缓存5分钟
                cache_manager.set_cached_data(cache_key, summary, 300)
            
            return render_template('index.html', summary=summary)
        except Exception as e:
            logger.error(f"首页加载失败: {e}")
            flash(f'数据加载失败: {str(e)}', 'error')
            return render_template('index.html', summary={})
    
    @app.route('/rankings')
    def rankings():
        """排行榜页面"""
        rank_type = request.args.get('type', 'topsellers')
        limit = min(int(request.args.get('limit', 50)), app.config['MAX_ITEMS_PER_PAGE'])
        
        try:
            cache_key = f'rankings_{rank_type}_{limit}'
            games = cache_manager.get_cached_data(cache_key)
            
            if not games:
                games = steam_query.get_top_games_by_rank(rank_type, limit)
                cache_manager.set_cached_data(cache_key, games, 180)  # 缓存3分钟
            
            return render_template('rankings.html', 
                                   games=games, 
                                   rank_type=rank_type,
                                   total_count=len(games))
        except Exception as e:
            logger.error(f"排行榜加载失败: {e}")
            flash(f'排行榜数据加载失败: {str(e)}', 'error')
            return render_template('rankings.html', games=[], rank_type=rank_type)
    
    @app.route('/analytics')
    def analytics():
        """数据分析页面"""
        return render_template('analytics.html')
    
    @app.route('/tables')
    def tables():
        """数据表管理页面"""
        try:
            available_tables = steam_query.get_available_tables()
            return render_template('tables.html', tables=available_tables)
        except Exception as e:
            logger.error(f"数据表页面加载失败: {e}")
            flash(f'数据表加载失败: {str(e)}', 'error')
            return render_template('tables.html', tables=[])
    
    @app.route('/api/stats/summary')
    def api_stats_summary():
        """API: 获取统计摘要"""
        try:
            cache_key = 'api_stats_summary'
            summary = cache_manager.get_cached_data(cache_key)
            
            if not summary:
                summary = steam_query.get_statistics_summary()
                cache_manager.set_cached_data(cache_key, summary, 300)
            
            return jsonify({
                'success': True,
                'data': summary,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"API统计摘要失败: {e}")
            return jsonify({
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500
    
    @app.route('/api/charts/price-distribution')
    def api_price_distribution():
        """API: 价格分布图表数据"""
        try:
            cache_key = 'chart_price_distribution'
            data = cache_manager.get_cached_data(cache_key)
            
            if not data:
                price_dist = steam_query.get_price_distribution()
                data = {
                    'labels': list(price_dist.keys()),
                    'values': list(price_dist.values()),
                    'colors': app.config['CHART_COLORS'][:len(price_dist)]
                }
                cache_manager.set_cached_data(cache_key, data, 600)  # 缓存10分钟
            
            return jsonify({
                'success': True,
                'data': data,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"价格分布API失败: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/charts/genre-distribution')
    def api_genre_distribution():
        """API: 游戏类型分布图表数据"""
        try:
            cache_key = 'chart_genre_distribution'
            data = cache_manager.get_cached_data(cache_key)
            
            if not data:
                genre_dist = steam_query.get_genre_distribution()
                data = {
                    'labels': list(genre_dist.keys()),
                    'values': list(genre_dist.values()),
                    'colors': app.config['CHART_COLORS'][:len(genre_dist)]
                }
                cache_manager.set_cached_data(cache_key, data, 600)
            
            return jsonify({
                'success': True,
                'data': data,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"游戏类型分布API失败: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/charts/discount-analysis')
    def api_discount_analysis():
        """API: 折扣分析图表数据"""
        try:
            cache_key = 'chart_discount_analysis'
            data = cache_manager.get_cached_data(cache_key)
            
            if not data:
                discount_data = steam_query.get_discount_analysis()
                data = {
                    'labels': list(discount_data.keys()),
                    'values': [v['count'] for v in discount_data.values()],
                    'avg_discounts': [v['avg_discount'] for v in discount_data.values()],
                    'colors': app.config['CHART_COLORS'][:len(discount_data)]
                }
                cache_manager.set_cached_data(cache_key, data, 600)
            
            return jsonify({
                'success': True,
                'data': data,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"折扣分析API失败: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/charts/trending')
    def api_trending_data():
        """API: 趋势数据"""
        try:
            days = int(request.args.get('days', 7))
            cache_key = f'chart_trending_{days}'
            data = cache_manager.get_cached_data(cache_key)
            
            if not data:
                data = steam_query.get_trending_data(days)
                cache_manager.set_cached_data(cache_key, data, 600)
            
            return jsonify({
                'success': True,
                'data': data,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"趋势数据API失败: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/games/latest')
    def api_latest_games():
        """API: 获取最新游戏数据"""
        try:
            limit = min(int(request.args.get('limit', 20)), app.config['MAX_ITEMS_PER_PAGE'])
            rank_type = request.args.get('rank_type', None)
            
            cache_key = f'latest_games_{limit}_{rank_type or "all"}'
            games = cache_manager.get_cached_data(cache_key)
            
            if not games:
                games = steam_query.get_latest_data(limit, rank_type)
                cache_manager.set_cached_data(cache_key, games, 180)
            
            return jsonify({
                'success': True,
                'data': games,
                'count': len(games),
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"最新游戏API失败: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/cache/clear')
    def api_clear_cache():
        """API: 清除缓存"""
        try:
            pattern = request.args.get('pattern', 'chart_*')
            cache_manager.delete_cache(pattern)
            
            return jsonify({
                'success': True,
                'message': f'缓存已清除 (pattern: {pattern})',
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"清除缓存失败: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.errorhandler(404)
    def not_found(error):
        """404错误处理"""
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """500错误处理"""
        logger.error(f"内部服务器错误: {error}")
        return render_template('errors/500.html'), 500
    
    @app.context_processor
    def inject_global_vars():
        """向模板注入全局变量"""
        return {
            'app_name': 'GameMarket Dashboard',
            'current_time': datetime.now(),
            'version': '1.0.0'
        }
    
    # 配置日志
    if not app.debug:
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not os.path.exists('data/logs'):
            os.makedirs('data/logs')
        
        file_handler = RotatingFileHandler(
            'data/logs/web_app.log', 
            maxBytes=10240000, 
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Web应用启动')
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )