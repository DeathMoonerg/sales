# Import library
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Import fungsi dari config.py
from config import *

# Set konfigurasi halaman dashboard
st.set_page_config("Dashboard", page_icon="📊", layout="wide")  # Judul, ikon, tata letak lebar

# Ambil data pelanggan
result_customers = view_customers()

df_customers = pd.DataFrame(result_customers, columns=[
    "customer_id", "name", "email", "phone", "address", "birthdate", 
])

# Hitung usia dari birthdate
df_customers['birthdate'] = pd.to_datetime(df_customers['birthdate']) #merubah tipe string menjadi datetime
df_customers['Age'] = (datetime.now() - df_customers['birthdate']).dt.days // 365 # waktu sekarang - dt.days : mengambil jumlah harinya saja dari selisih tersebut / 365.

# Fungsi tampilkan tabel + export CSV
def tabelCustomers_dan_export():
    # Hitung jumlah pelanggan
    total_customers = df_customers.shape[0]

    # Tampilkan metrik
    col1, col2, col3 = st.columns(3) # Fungsi st.columns(3) membuat tiga kolom sejajar di tampilan web Streamlit, menjadi tiga bagian horizontal — col1, col2, dan col3.
    with col1:
        st.metric(label="📦 Total Pelanggan", value=total_customers, delta="Semua Data")

    # Sidebar: Filter Rentang Usia
    with st.sidebar.expander("🔍 Filter Data Pelanggan", expanded=True):
        st.markdown("**Filter Rentang Usia**")
        min_age = int(df_customers['Age'].min())
        max_age = int(df_customers['Age'].max())
        # Pastikan max_value > min_value
        if max_age <= min_age:
            max_age = min_age + 1
        age_range = st.slider(
        "Pilih Rentang Usia",
            min_value=min_age,
            max_value=max_age,
            value=(min_age, max_age),
            help="Geser untuk memilih rentang usia yang ingin ditampilkan"
    )

    # Terapkan filter usia
    filtered_df = df_customers[df_customers['Age'].between(*age_range)]

    # Tampilkan tabel pelanggan
    st.markdown("### 📋 Tabel Data Pelanggan")
    
    showdata = st.multiselect( # menampilkan daftar kolom dari filtered_df yang bisa dipilih pengguna.
        "Pilih Kolom Pelanggan yang Ditampilkan",
        options=filtered_df.columns, # menampilkan semua nama kolom yang tersedia.
        default=["customer_id", "name", "email", "phone", "address", "birthdate", "Age"]
    )
    
    # Menampilkan tabel data pelanggan ke layar dengan hanya kolom yang dipilih (showdata).
    # use_container_width=True membuat tabel otomatis menyesuaikan lebar layar (responsif).
    st.dataframe(filtered_df[showdata], use_container_width=True) 

# Mendefinisikan fungsi helper untuk mengubah DataFrame menjadi file CSV.
# @st.cache_data adalah decorator Streamlit agar fungsi ini tidak dijalankan ulang setiap kali halaman di-refresh
# _df.to_csv(index=False) mengubah DataFrame menjadi teks CSV tanpa kolom indeks.
# membuat hasilnya bisa diunduh dengan karakter yang benar

    @st.cache_data
    def convert_df_to_csv(_df):
        return _df.to_csv(index=False).encode('utf-8')
    
    csv = convert_df_to_csv(filtered_df[showdata])
    st.download_button(
        label="⬇️ Download Data Pelanggan sebagai CSV",
        data=csv,
        file_name='data_pelanggan.csv',
        mime='text/csv'
    )

# ============================================
# FUNGSI VISUALISASI PRODUCTS
# ============================================
def visualisasiProducts():
    # Ambil data products
    result_products = view_products()
    df_products = pd.DataFrame(result_products, columns=[
        "product_id", "name", "description", "price", "stock"
    ])
    
    # Konversi ke numeric
    df_products['price'] = pd.to_numeric(df_products['price'], errors='coerce')
    df_products['stock'] = pd.to_numeric(df_products['stock'], errors='coerce')
    
    # Filter di sidebar
    with st.sidebar.expander("🔍 Filter Data Produk", expanded=True):
        st.markdown("**Filter Rentang Harga**")
        min_price = float(df_products['price'].min())
        max_price = float(df_products['price'].max())
        # Pastikan max_value > min_value
        if max_price <= min_price:
            max_price = min_price + 1000.0
        price_range = st.slider(
            "Pilih Rentang Harga (Rp)",
            min_value=min_price,
            max_value=max_price,
            value=(min_price, max_price),
            step=100000.0,
            format="Rp %d",
            help="Geser untuk memilih rentang harga produk yang ingin ditampilkan"
        )
        
        st.markdown("---")
        st.markdown("**Filter Rentang Stok**")
        min_stock = int(df_products['stock'].min())
        max_stock = int(df_products['stock'].max())
        # Pastikan max_value > min_value
        if max_stock <= min_stock:
            max_stock = min_stock + 1
        stock_range = st.slider(
            "Pilih Rentang Stok",
            min_value=min_stock,
            max_value=max_stock,
            value=(min_stock, max_stock),
            help="Geser untuk memilih rentang stok produk yang ingin ditampilkan"
        )
        
        st.markdown("---")
        st.markdown("**⚙️ Pengaturan Stok Rendah**")
        threshold_stok_rendah = st.number_input(
            "Threshold Stok Rendah",
            min_value=0,
            max_value=int(max_stock),
            value=20,
            step=1,
            help="Produk dengan stok di bawah nilai ini akan dianggap stok rendah"
        )
    
    # Terapkan filter
    filtered_products = df_products[
        (df_products['price'] >= price_range[0]) & 
        (df_products['price'] <= price_range[1]) &
        (df_products['stock'] >= stock_range[0]) & 
        (df_products['stock'] <= stock_range[1])
    ]
    
    # Hitung produk dengan stok rendah
    produk_stok_rendah = filtered_products[filtered_products['stock'] < threshold_stok_rendah]
    jumlah_stok_rendah = len(produk_stok_rendah)
    
    # Metrik (menggunakan data yang sudah difilter)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("📦 Total Produk", filtered_products.shape[0])
    with col2:
        st.metric("💰 Harga Rata-rata", f"Rp {filtered_products['price'].mean():,.0f}")
    with col3:
        st.metric("📊 Total Stok", filtered_products['stock'].sum())
    with col4:
        st.metric("💵 Nilai Inventori", f"Rp {(filtered_products['price'] * filtered_products['stock']).sum():,.0f}")
    with col5:
        # Warna merah jika ada stok rendah
        delta_color = "inverse" if jumlah_stok_rendah > 0 else "normal"
        st.metric(
            "⚠️ Stok Rendah", 
            jumlah_stok_rendah,
            delta=f"< {threshold_stok_rendah} unit",
            delta_color=delta_color
        )
    
    # Alert untuk stok rendah
    if jumlah_stok_rendah > 0:
        st.warning(f"⚠️ **Peringatan:** Ada {jumlah_stok_rendah} produk dengan stok rendah (di bawah {threshold_stok_rendah} unit)!")
        
        # Tampilkan daftar produk stok rendah
        with st.expander(f"📋 Lihat Daftar Produk Stok Rendah ({jumlah_stok_rendah} produk)", expanded=False):
            st.dataframe(
                produk_stok_rendah[['product_id', 'name', 'stock', 'price']].sort_values('stock'),
                use_container_width=True,
                hide_index=True
            )
    
    # Info filter aktif
    if len(filtered_products) < len(df_products):
        st.info(f"📊 Menampilkan {len(filtered_products)} dari {len(df_products)} produk berdasarkan filter yang dipilih")
    
    st.markdown("---")
    
    # Tabs untuk berbagai visualisasi
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Grafik", "📋 Tabel", "📈 Analisis Harga", "📦 Analisis Stok"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Bar chart harga produk (menggunakan data filtered)
            fig_price = px.bar(
                filtered_products.sort_values('price', ascending=False).head(10),
                x='name',
                y='price',
                title='Top 10 Produk Berdasarkan Harga',
                labels={'name': 'Nama Produk', 'price': 'Harga (Rp)'},
                color='price',
                color_continuous_scale='Blues'
            )
            fig_price.update_xaxes(tickangle=-45)
            st.plotly_chart(fig_price, use_container_width=True)
        
        with col2:
            # Pie chart distribusi stok (menggunakan data filtered)
            fig_stock = px.pie(
                filtered_products,
                values='stock',
                names='name',
                title='Distribusi Stok Produk',
                hole=0.4
            )
            st.plotly_chart(fig_stock, use_container_width=True)
        
        # Scatter plot harga vs stok (menggunakan data filtered)
        fig_scatter = px.scatter(
            filtered_products,
            x='price',
            y='stock',
            size=np.array(filtered_products['stock'], dtype=float),
            color='price',
            hover_name='name',
            title='Hubungan Harga vs Stok Produk',
            labels={'price': 'Harga (Rp)', 'stock': 'Stok'}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with tab2:
        st.markdown("### 📋 Tabel Data Produk")
        showdata_products = st.multiselect(
            "Pilih Kolom yang Ditampilkan",
            options=filtered_products.columns,
            default=["product_id", "name", "price", "stock"]
        )
        
        # Tambahkan kolom status stok untuk highlight
        display_df = filtered_products[showdata_products].copy()
        if 'stock' in display_df.columns:
            display_df['Status Stok'] = display_df['stock'].apply(
                lambda x: '⚠️ Rendah' if x < threshold_stok_rendah else '✅ Normal'
            )
        
        # Tampilkan tabel dengan styling
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Info tentang stok rendah
        if jumlah_stok_rendah > 0 and 'stock' in display_df.columns:
            st.info(f"💡 Produk dengan status '⚠️ Rendah' memiliki stok di bawah {threshold_stok_rendah} unit")
        
        # Export CSV
        @st.cache_data
        def convert_df_to_csv(_df):
            return _df.to_csv(index=False).encode('utf-8')
        
        csv = convert_df_to_csv(filtered_products[showdata_products])
        st.download_button(
            label="⬇️ Download Data Produk sebagai CSV",
            data=csv,
            file_name='data_produk.csv',
            mime='text/csv'
        )
    
    with tab3:
        # Histogram harga (menggunakan data filtered)
        fig_hist = px.histogram(
            filtered_products,
            x='price',
            nbins=20,
            title='Distribusi Harga Produk',
            labels={'price': 'Harga (Rp)', 'count': 'Jumlah Produk'}
        )
        st.plotly_chart(fig_hist, use_container_width=True)
        
        # Box plot harga (menggunakan data filtered)
        fig_box = px.box(
            filtered_products,
            y='price',
            title='Box Plot Harga Produk',
            labels={'price': 'Harga (Rp)'}
        )
        st.plotly_chart(fig_box, use_container_width=True)
    
    with tab4:
        col1, col2 = st.columns(2)
        
        with col1:
            # Bar chart stok terendah (menggunakan data filtered) - Horizontal
            fig_low_stock = px.bar(
                filtered_products.nsmallest(10, 'stock'),
                x='stock',
                y='name',
                orientation='h',
                title='10 Produk dengan Stok Terendah',
                labels={'name': 'Nama Produk', 'stock': 'Stok'},
                color='stock',
                color_continuous_scale='Reds'
            )
            fig_low_stock.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_low_stock, use_container_width=True)
        
        with col2:
            # Bar chart produk stok rendah (berdasarkan threshold) - Horizontal
            if jumlah_stok_rendah > 0:
                fig_stok_rendah = px.bar(
                    produk_stok_rendah.sort_values('stock'),
                    x='stock',
                    y='name',
                    orientation='h',
                    title=f'Produk dengan Stok Rendah (< {threshold_stok_rendah} unit)',
                    labels={'name': 'Nama Produk', 'stock': 'Stok'},
                    color='stock',
                    color_continuous_scale='Oranges'
                )
                fig_stok_rendah.update_layout(yaxis={'categoryorder': 'total ascending'})
                fig_stok_rendah.add_vline(
                    x=threshold_stok_rendah,
                    line_dash="dash",
                    line_color="red",
                    annotation_text=f"Threshold: {threshold_stok_rendah}",
                    annotation_position="top"
                )
                st.plotly_chart(fig_stok_rendah, use_container_width=True)
            else:
                st.success(f"✅ Tidak ada produk dengan stok rendah (semua produk memiliki stok ≥ {threshold_stok_rendah} unit)")
        
        # Tabel detail produk stok rendah
        if jumlah_stok_rendah > 0:
            st.markdown("### 📊 Detail Produk Stok Rendah")
            detail_stok_rendah = produk_stok_rendah[['product_id', 'name', 'stock', 'price']].copy()
            detail_stok_rendah['Nilai Inventori'] = detail_stok_rendah['price'] * detail_stok_rendah['stock']
            detail_stok_rendah = detail_stok_rendah.sort_values('stock')
            st.dataframe(detail_stok_rendah, use_container_width=True, hide_index=True)

# ============================================
# FUNGSI VISUALISASI ORDERS
# ============================================
def visualisasiOrders():
    # Ambil data orders
    result_orders = view_orders_with_customers()
    df_orders = pd.DataFrame(result_orders, columns=[
        "order_id", "order_date", "total_amount", "customer_name", "phone"
    ])
    
    # Konversi order_date ke datetime
    df_orders['order_date'] = pd.to_datetime(df_orders['order_date'])
    df_orders['month'] = df_orders['order_date'].dt.to_period('M').astype(str)
    df_orders['day'] = df_orders['order_date'].dt.date
    
    # Konversi total_amount ke numeric
    df_orders['total_amount'] = pd.to_numeric(df_orders['total_amount'], errors='coerce')
    
    # Filter di sidebar
    with st.sidebar.expander("🔍 Filter Data Pesanan", expanded=True):
        st.markdown("**Filter Rentang Tanggal**")
        date_range = st.date_input(
            "Pilih Rentang Tanggal",
            value=(df_orders['day'].min(), df_orders['day'].max()),
            min_value=df_orders['day'].min(),
            max_value=df_orders['day'].max(),
            help="Pilih tanggal mulai dan akhir untuk memfilter data pesanan"
        )
        
        st.markdown("---")
        st.markdown("**Filter Rentang Total Amount**")
        min_amount = float(df_orders['total_amount'].min())
        max_amount = float(df_orders['total_amount'].max())
        # Pastikan max_value > min_value
        if max_amount <= min_amount:
            max_amount = min_amount + 1000.0
        amount_range = st.slider(
            "Pilih Rentang Total Amount (Rp)",
            min_value=min_amount,
            max_value=max_amount,
            value=(min_amount, max_amount),
            step=100000.0,
            format="Rp %d",
            help="Geser untuk memilih rentang total amount yang ingin ditampilkan"
        )
    
    # Terapkan filter
    filtered_orders = df_orders.copy()
    
    # Filter tanggal
    if len(date_range) == 2:
        filtered_orders = filtered_orders[
            (filtered_orders['day'] >= date_range[0]) & 
            (filtered_orders['day'] <= date_range[1])
        ]
    
    # Filter total amount
    filtered_orders = filtered_orders[
        (filtered_orders['total_amount'] >= amount_range[0]) & 
        (filtered_orders['total_amount'] <= amount_range[1])
    ]
    
    # Metrik (menggunakan data yang sudah difilter)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📦 Total Pesanan", filtered_orders.shape[0])
    with col2:
        st.metric("💰 Total Pendapatan", f"Rp {filtered_orders['total_amount'].sum():,.0f}")
    with col3:
        st.metric("📊 Rata-rata Pesanan", f"Rp {filtered_orders['total_amount'].mean():,.0f}")
    with col4:
        st.metric("📈 Pesanan Tertinggi", f"Rp {filtered_orders['total_amount'].max():,.0f}")
    
    # Info filter aktif
    if len(filtered_orders) < len(df_orders):
        st.info(f"📊 Menampilkan {len(filtered_orders)} dari {len(df_orders)} pesanan berdasarkan filter yang dipilih")
    
    st.markdown("---")
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Grafik", "📋 Tabel", "📈 Trend Waktu", "👥 Analisis Pelanggan"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Line chart pendapatan per bulan (menggunakan data filtered)
            monthly_revenue = filtered_orders.groupby('month')['total_amount'].sum().reset_index()
            fig_monthly = px.line(
                monthly_revenue,
                x='month',
                y='total_amount',
                title='Pendapatan per Bulan',
                labels={'month': 'Bulan', 'total_amount': 'Pendapatan (Rp)'},
                markers=True
            )
            st.plotly_chart(fig_monthly, use_container_width=True)
        
        with col2:
            # Bar chart jumlah pesanan per bulan (menggunakan data filtered)
            monthly_orders = filtered_orders.groupby('month')['order_id'].count().reset_index()
            monthly_orders.columns = ['month', 'jumlah_pesanan']
            fig_orders = px.bar(
                monthly_orders,
                x='month',
                y='jumlah_pesanan',
                title='Jumlah Pesanan per Bulan',
                labels={'month': 'Bulan', 'jumlah_pesanan': 'Jumlah Pesanan'},
                color='jumlah_pesanan',
                color_continuous_scale='Greens'
            )
            st.plotly_chart(fig_orders, use_container_width=True)
        
        # Scatter plot order date vs total amount (menggunakan data filtered)
        fig_scatter = px.scatter(
            filtered_orders,
            x='order_date',
            y='total_amount',
            size=np.array(filtered_orders['total_amount'], dtype=float),
            color='total_amount',
            hover_name='customer_name',
            title='Pesanan Berdasarkan Tanggal dan Jumlah',
            labels={'order_date': 'Tanggal Pesanan', 'total_amount': 'Total (Rp)'}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with tab2:
        st.markdown("### 📋 Tabel Data Pesanan")
        
        showdata_orders = st.multiselect(
            "Pilih Kolom yang Ditampilkan",
            options=filtered_orders.columns,
            default=["order_id", "order_date", "customer_name", "total_amount"]
        )
        st.dataframe(filtered_orders[showdata_orders], use_container_width=True)
        
        # Export CSV
        @st.cache_data
        def convert_df_to_csv(_df):
            return _df.to_csv(index=False).encode('utf-8')
        
        csv = convert_df_to_csv(filtered_orders[showdata_orders])
        st.download_button(
            label="⬇️ Download Data Pesanan sebagai CSV",
            data=csv,
            file_name='data_pesanan.csv',
            mime='text/csv'
        )
    
    with tab3:
        # Line chart trend harian (menggunakan data filtered)
        daily_revenue = filtered_orders.groupby('day')['total_amount'].sum().reset_index()
        fig_daily = px.line(
            daily_revenue,
            x='day',
            y='total_amount',
            title='Trend Pendapatan Harian',
            labels={'day': 'Tanggal', 'total_amount': 'Pendapatan (Rp)'},
            markers=True
        )
        st.plotly_chart(fig_daily, use_container_width=True)
    
    with tab4:
        # Top 10 pelanggan berdasarkan total pembelian (menggunakan data filtered)
        customer_stats = filtered_orders.groupby('customer_name').agg({
            'order_id': 'count',
            'total_amount': 'sum'
        }).reset_index()
        customer_stats.columns = ['customer_name', 'jumlah_pesanan', 'total_pembelian']
        customer_stats = customer_stats.sort_values('total_pembelian', ascending=False).head(10)
        
        fig_customers = px.bar(
            customer_stats,
            x='customer_name',
            y='total_pembelian',
            title='Top 10 Pelanggan Berdasarkan Total Pembelian',
            labels={'customer_name': 'Nama Pelanggan', 'total_pembelian': 'Total Pembelian (Rp)'},
            color='total_pembelian',
            color_continuous_scale='Purples'
        )
        fig_customers.update_xaxes(tickangle=-45)
        st.plotly_chart(fig_customers, use_container_width=True)

# ============================================
# FUNGSI VISUALISASI ORDER DETAILS
# ============================================
def visualisasiOrderDetails():
    # Ambil data order details
    result_order_details = view_order_details_with_info()
    df_order_details = pd.DataFrame(result_order_details, columns=[
        "order_detail_id", "order_id", "order_date", "customer_id", "customer_name",
        "product_id", "product_name", "unit_price", "quantity", "subtotal",
        "order_total", "phone"
    ])
    
    # Konversi order_date ke datetime
    df_order_details['order_date'] = pd.to_datetime(df_order_details['order_date'])
    df_order_details['day'] = df_order_details['order_date'].dt.date
    
    # Konversi kolom numeric
    df_order_details['subtotal'] = pd.to_numeric(df_order_details['subtotal'], errors='coerce')
    df_order_details['quantity'] = pd.to_numeric(df_order_details['quantity'], errors='coerce')
    df_order_details['unit_price'] = pd.to_numeric(df_order_details['unit_price'], errors='coerce')
    
    # Filter di sidebar
    with st.sidebar.expander("🔍 Filter Data Detail Pesanan", expanded=True):
        st.markdown("**Filter berdasarkan Produk**")
        product_filter = st.multiselect(
            "Pilih Produk",
            options=sorted(df_order_details['product_name'].unique()),
            default=[],
            help="Pilih satu atau lebih produk untuk memfilter data"
        )
        
        st.markdown("---")
        st.markdown("**Filter Rentang Tanggal**")
        date_range = st.date_input(
            "Pilih Rentang Tanggal",
            value=(df_order_details['day'].min(), df_order_details['day'].max()),
            min_value=df_order_details['day'].min(),
            max_value=df_order_details['day'].max(),
            help="Pilih tanggal mulai dan akhir untuk memfilter data"
        )
        
        st.markdown("---")
        st.markdown("**Filter Rentang Quantity**")
        min_qty = int(df_order_details['quantity'].min())
        max_qty = int(df_order_details['quantity'].max())
        # Pastikan max_value > min_value
        if max_qty <= min_qty:
            max_qty = min_qty + 1
        qty_range = st.slider(
            "Pilih Rentang Quantity",
            min_value=min_qty,
            max_value=max_qty,
            value=(min_qty, max_qty),
            help="Geser untuk memilih rentang quantity yang ingin ditampilkan"
        )
        
        st.markdown("---")
        st.markdown("**Filter Rentang Subtotal**")
        min_subtotal = float(df_order_details['subtotal'].min())
        max_subtotal = float(df_order_details['subtotal'].max())
        # Pastikan max_value > min_value
        if max_subtotal <= min_subtotal:
            max_subtotal = min_subtotal + 1000.0
        subtotal_range = st.slider(
            "Pilih Rentang Subtotal (Rp)",
            min_value=min_subtotal,
            max_value=max_subtotal,
            value=(min_subtotal, max_subtotal),
            step=100000.0,
            format="Rp %d",
            help="Geser untuk memilih rentang subtotal yang ingin ditampilkan"
        )
    
    # Terapkan filter
    filtered_details = df_order_details.copy()
    
    # Filter produk
    if product_filter:
        filtered_details = filtered_details[filtered_details['product_name'].isin(product_filter)]
    
    # Filter tanggal
    if len(date_range) == 2:
        filtered_details = filtered_details[
            (filtered_details['day'] >= date_range[0]) & 
            (filtered_details['day'] <= date_range[1])
        ]
    
    # Filter quantity
    filtered_details = filtered_details[
        (filtered_details['quantity'] >= qty_range[0]) & 
        (filtered_details['quantity'] <= qty_range[1])
    ]
    
    # Filter subtotal
    filtered_details = filtered_details[
        (filtered_details['subtotal'] >= subtotal_range[0]) & 
        (filtered_details['subtotal'] <= subtotal_range[1])
    ]
    
    # Metrik (menggunakan data yang sudah difilter)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📦 Total Item Terjual", int(filtered_details['quantity'].sum()))
    with col2:
        st.metric("💰 Total Revenue", f"Rp {filtered_details['subtotal'].sum():,.0f}")
    with col3:
        st.metric("📊 Rata-rata Quantity", f"{filtered_details['quantity'].mean():.2f}")
    with col4:
        st.metric("🛍️ Produk Unik Terjual", filtered_details['product_name'].nunique())
    
    # Info filter aktif
    if len(filtered_details) < len(df_order_details):
        st.info(f"📊 Menampilkan {len(filtered_details)} dari {len(df_order_details)} detail pesanan berdasarkan filter yang dipilih")
    
    st.markdown("---")
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Grafik", "📋 Tabel", "🏆 Produk Terlaris", "📈 Analisis Penjualan"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Top 10 produk terlaris berdasarkan quantity (menggunakan data filtered)
            top_products = filtered_details.groupby('product_name')['quantity'].sum().reset_index()
            top_products = top_products.sort_values('quantity', ascending=False).head(10)
            
            fig_top = px.bar(
                top_products,
                x='product_name',
                y='quantity',
                title='Top 10 Produk Terlaris (Berdasarkan Quantity)',
                labels={'product_name': 'Nama Produk', 'quantity': 'Jumlah Terjual'},
                color='quantity',
                color_continuous_scale='Oranges'
            )
            fig_top.update_xaxes(tickangle=-45)
            st.plotly_chart(fig_top, use_container_width=True)
        
        with col2:
            # Top 10 produk berdasarkan revenue (menggunakan data filtered)
            top_revenue = filtered_details.groupby('product_name')['subtotal'].sum().reset_index()
            top_revenue = top_revenue.sort_values('subtotal', ascending=False).head(10)
            
            fig_revenue = px.bar(
                top_revenue,
                x='product_name',
                y='subtotal',
                title='Top 10 Produk Berdasarkan Revenue',
                labels={'product_name': 'Nama Produk', 'subtotal': 'Revenue (Rp)'},
                color='subtotal',
                color_continuous_scale='Blues'
            )
            fig_revenue.update_xaxes(tickangle=-45)
            st.plotly_chart(fig_revenue, use_container_width=True)
        
        # Scatter plot quantity vs subtotal (menggunakan data filtered)
        fig_scatter = px.scatter(
            filtered_details,
            x='quantity',
            y='subtotal',
            size=np.array(filtered_details['subtotal'], dtype=float),
            color='product_name',
            hover_name='product_name',
            title='Hubungan Quantity vs Subtotal',
            labels={'quantity': 'Quantity', 'subtotal': 'Subtotal (Rp)'}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with tab2:
        st.markdown("### 📋 Tabel Data Detail Pesanan")
        
        showdata_details = st.multiselect(
            "Pilih Kolom yang Ditampilkan",
            options=filtered_details.columns,
            default=["order_id", "order_date", "customer_name", "product_name", "quantity", "subtotal"]
        )
        st.dataframe(filtered_details[showdata_details], use_container_width=True)
        
        # Export CSV
        @st.cache_data
        def convert_df_to_csv(_df):
            return _df.to_csv(index=False).encode('utf-8')
        
        csv = convert_df_to_csv(filtered_details[showdata_details])
        st.download_button(
            label="⬇️ Download Data Detail Pesanan sebagai CSV",
            data=csv,
            file_name='data_detail_pesanan.csv',
            mime='text/csv'
        )
    
    with tab3:
        # Pie chart distribusi penjualan produk (menggunakan data filtered)
        product_sales = filtered_details.groupby('product_name')['quantity'].sum().reset_index()
        fig_pie = px.pie(
            product_sales,
            values='quantity',
            names='product_name',
            title='Distribusi Penjualan Produk (Berdasarkan Quantity)',
            hole=0.4
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Tabel produk terlaris (menggunakan data filtered)
        st.markdown("### 🏆 Ranking Produk Terlaris")
        product_stats = filtered_details.groupby('product_name').agg({
            'quantity': 'sum',
            'subtotal': 'sum',
            'order_id': 'count'
        }).reset_index()
        product_stats.columns = ['Nama Produk', 'Total Terjual', 'Total Revenue (Rp)', 'Jumlah Pesanan']
        product_stats = product_stats.sort_values('Total Terjual', ascending=False)
        st.dataframe(product_stats, use_container_width=True)
    
    with tab4:
        # Analisis penjualan per hari (menggunakan data filtered)
        daily_sales = filtered_details.groupby(filtered_details['order_date'].dt.date).agg({
            'quantity': 'sum',
            'subtotal': 'sum'
        }).reset_index()
        daily_sales.columns = ['tanggal', 'total_quantity', 'total_revenue']
        
        col1, col2 = st.columns(2)
        with col1:
            fig_qty = px.line(
                daily_sales,
                x='tanggal',
                y='total_quantity',
                title='Trend Quantity Terjual per Hari',
                labels={'tanggal': 'Tanggal', 'total_quantity': 'Total Quantity'},
                markers=True
            )
            st.plotly_chart(fig_qty, use_container_width=True)
        
        with col2:
            fig_rev = px.line(
                daily_sales,
                x='tanggal',
                y='total_revenue',
                title='Trend Revenue per Hari',
                labels={'tanggal': 'Tanggal', 'total_revenue': 'Total Revenue (Rp)'},
                markers=True
            )
            st.plotly_chart(fig_rev, use_container_width=True)

# ============================================
# SIDEBAR NAVIGASI
# ============================================
st.sidebar.title("📊 Dashboard Menu")
st.sidebar.markdown("---")

# Inisialisasi session state untuk halaman aktif
if 'active_page' not in st.session_state:
    st.session_state.active_page = "🏠 Beranda"

st.sidebar.markdown("**Pilih Halaman:**")

# Inisialisasi checkbox state jika belum ada (SEBELUM widget dibuat)
if 'beranda' not in st.session_state:
    st.session_state.beranda = (st.session_state.active_page == "🏠 Beranda")
if 'pelanggan' not in st.session_state:
    st.session_state.pelanggan = (st.session_state.active_page == "👥 Pelanggan")
if 'produk' not in st.session_state:
    st.session_state.produk = (st.session_state.active_page == "📦 Produk")
if 'pesanan' not in st.session_state:
    st.session_state.pesanan = (st.session_state.active_page == "🛒 Pesanan")
if 'detail_pesanan' not in st.session_state:
    st.session_state.detail_pesanan = (st.session_state.active_page == "📋 Detail Pesanan")

# Pastikan setidaknya satu checkbox tercentang (SEBELUM widget dibuat)
if not (st.session_state.beranda or st.session_state.pelanggan or 
        st.session_state.produk or st.session_state.pesanan or st.session_state.detail_pesanan):
    st.session_state.active_page = "🏠 Beranda"
    st.session_state.beranda = True

# Fungsi callback untuk update halaman aktif (eksklusif - hanya satu yang aktif)
def update_page_beranda():
    if st.session_state.beranda:
        st.session_state.active_page = "🏠 Beranda"
        st.session_state.pelanggan = False
        st.session_state.produk = False
        st.session_state.pesanan = False
        st.session_state.detail_pesanan = False

def update_page_pelanggan():
    if st.session_state.pelanggan:
        st.session_state.active_page = "👥 Pelanggan"
        st.session_state.beranda = False
        st.session_state.produk = False
        st.session_state.pesanan = False
        st.session_state.detail_pesanan = False

def update_page_produk():
    if st.session_state.produk:
        st.session_state.active_page = "📦 Produk"
        st.session_state.beranda = False
        st.session_state.pelanggan = False
        st.session_state.pesanan = False
        st.session_state.detail_pesanan = False

def update_page_pesanan():
    if st.session_state.pesanan:
        st.session_state.active_page = "🛒 Pesanan"
        st.session_state.beranda = False
        st.session_state.pelanggan = False
        st.session_state.produk = False
        st.session_state.detail_pesanan = False

def update_page_detail():
    if st.session_state.detail_pesanan:
        st.session_state.active_page = "📋 Detail Pesanan"
        st.session_state.beranda = False
        st.session_state.pelanggan = False
        st.session_state.produk = False
        st.session_state.pesanan = False

# Checkbox untuk setiap halaman dengan callback
beranda = st.sidebar.checkbox(
    "🏠 Beranda", 
    value=st.session_state.beranda, 
    key="beranda",
    on_change=update_page_beranda
)
pelanggan = st.sidebar.checkbox(
    "👥 Pelanggan", 
    value=st.session_state.pelanggan, 
    key="pelanggan",
    on_change=update_page_pelanggan
)
produk = st.sidebar.checkbox(
    "📦 Produk", 
    value=st.session_state.produk, 
    key="produk",
    on_change=update_page_produk
)
pesanan = st.sidebar.checkbox(
    "🛒 Pesanan", 
    value=st.session_state.pesanan, 
    key="pesanan",
    on_change=update_page_pesanan
)
detail_pesanan = st.sidebar.checkbox(
    "📋 Detail Pesanan", 
    value=st.session_state.detail_pesanan, 
    key="detail_pesanan",
    on_change=update_page_detail
)

# Tentukan halaman aktif berdasarkan checkbox
page = st.session_state.active_page

if page == "🏠 Beranda":
    st.title("🏠 Dashboard Sales Database")
    st.markdown("---")
    st.markdown("""
    ### Selamat Datang di Dashboard Sales Database!
    
    Dashboard ini menampilkan visualisasi dan analisis data dari database sales yang terdiri dari:
    - **Pelanggan (Customers)**: Data pelanggan dengan filter usia
    - **Produk (Products)**: Data produk dengan analisis harga dan stok
    - **Pesanan (Orders)**: Data pesanan dengan trend waktu dan analisis pelanggan
    - **Detail Pesanan (Order Details)**: Detail item pesanan dengan analisis produk terlaris
    
    **Fitur:**
    - 📊 Visualisasi interaktif dengan Plotly
    - 📋 Tabel data dengan filter
    - ⬇️ Export data ke CSV
    - 📈 Analisis trend dan statistik
    """)
    
    # Statistik ringkas
    st.markdown("### 📊 Statistik Ringkas")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👥 Total Pelanggan", df_customers.shape[0])
    
    result_products = view_products()
    df_products = pd.DataFrame(result_products, columns=[
        "product_id", "name", "description", "price", "stock"
    ])
    with col2:
        st.metric("📦 Total Produk", df_products.shape[0])
    
    result_orders = view_orders_with_customers()
    df_orders = pd.DataFrame(result_orders, columns=[
        "order_id", "order_date", "total_amount", "customer_name", "phone"
    ])
    with col3:
        st.metric("🛒 Total Pesanan", df_orders.shape[0])
    
    with col4:
        st.metric("💰 Total Revenue", f"Rp {df_orders['total_amount'].sum():,.0f}")

elif page == "👥 Pelanggan":
    st.title("👥 Data Pelanggan")
    st.markdown("---")
    tabelCustomers_dan_export()

elif page == "📦 Produk":
    st.title("📦 Data Produk")
    st.markdown("---")
    visualisasiProducts()

elif page == "🛒 Pesanan":
    st.title("🛒 Data Pesanan")
    st.markdown("---")
    visualisasiOrders()

elif page == "📋 Detail Pesanan":
    st.title("📋 Data Detail Pesanan")
    st.markdown("---")
    visualisasiOrderDetails()