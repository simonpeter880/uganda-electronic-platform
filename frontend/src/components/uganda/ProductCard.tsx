"use client";

import { useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { Heart, ShoppingCart, Eye, TrendingUp } from "lucide-react";

interface ProductCardProps {
	id: string;
	name: string;
	slug: string;
	price: number;
	originalPrice?: number;
	image: string;
	rating?: number;
	reviewCount?: number;
	stockCount?: number;
	soldToday?: number;
	deliveryFee?: number;
	isFlashDeal?: boolean;
	flashDealEndsAt?: Date;
	badge?: string;
	installmentPrice?: number;
}

export default function ProductCard({
	id,
	name,
	slug,
	price,
	originalPrice,
	image,
	rating = 0,
	reviewCount = 0,
	stockCount,
	soldToday,
	deliveryFee,
	isFlashDeal = false,
	flashDealEndsAt,
	badge,
	installmentPrice,
}: ProductCardProps) {
	const [isWishlisted, setIsWishlisted] = useState(false);
	const [isHovered, setIsHovered] = useState(false);

	const discountPercentage = originalPrice
		? Math.round(((originalPrice - price) / originalPrice) * 100)
		: 0;

	const formatPrice = (amount: number) => {
		return new Intl.NumberFormat("en-UG", {
			style: "currency",
			currency: "UGX",
			minimumFractionDigits: 0,
		}).format(amount);
	};

	return (
		<div
			className="group relative bg-white rounded-xl overflow-hidden shadow-sm hover:shadow-lg transition-all duration-300 border border-gray-100"
			onMouseEnter={() => setIsHovered(true)}
			onMouseLeave={() => setIsHovered(false)}
		>
			{/* Badges */}
			<div className="absolute top-2 left-2 z-10 flex flex-col gap-1">
				{isFlashDeal && (
					<span className="bg-error-500 text-white text-xs font-bold px-2.5 py-1 rounded-full animate-pulse shadow-md">
						⚡ FLASH DEAL
					</span>
				)}
				{discountPercentage > 0 && (
					<span className="bg-primary-500 text-white text-xs font-bold px-2.5 py-1 rounded-full shadow-md">
						-{discountPercentage}%
					</span>
				)}
				{badge && (
					<span className="bg-success-500 text-gray-900 text-xs font-bold px-2.5 py-1 rounded-full shadow-md">
						{badge}
					</span>
				)}
			</div>

			{/* Wishlist Button */}
			<button
				onClick={() => setIsWishlisted(!isWishlisted)}
				className="absolute top-2 right-2 z-10 bg-white/90 backdrop-blur-sm p-2 rounded-full shadow-md hover:bg-white transition-colors"
				aria-label="Add to wishlist"
			>
				<Heart
					size={20}
					className={`${isWishlisted ? "fill-error-500 text-error-500" : "text-gray-600"} transition-colors`}
				/>
			</button>

			{/* Product Image */}
			<Link href={`/product/${slug}`}>
				<div className="relative aspect-square bg-gray-50 overflow-hidden">
					<Image
						src={image}
						alt={name}
						fill
						className="object-cover group-hover:scale-110 transition-transform duration-500"
						sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, 25vw"
					/>

					{/* Quick Actions Overlay */}
					{isHovered && (
						<div className="absolute inset-0 bg-black/30 flex items-center justify-center gap-3 animate-fade-in">
							<button
								className="bg-white text-primary-500 p-3 rounded-full hover:bg-primary-500 hover:text-white transition-all shadow-lg"
								aria-label="Quick view"
							>
								<Eye size={20} />
							</button>
							<button
								className="bg-primary-500 text-white p-3 rounded-full hover:bg-primary-600 transition-all shadow-lg"
								aria-label="Add to cart"
							>
								<ShoppingCart size={20} />
							</button>
						</div>
					)}
				</div>
			</Link>

			{/* Product Info */}
			<div className="p-4">
				{/* Urgency Indicators */}
				{(stockCount || soldToday) && (
					<div className="flex flex-wrap gap-2 mb-2">
						{stockCount && stockCount <= 5 && (
							<span className="text-xs text-error-500 font-medium flex items-center gap-1">
								<TrendingUp size={12} />
								Only {stockCount} left!
							</span>
						)}
						{soldToday && soldToday > 0 && (
							<span className="text-xs text-gray-600">
								🔥 {soldToday} sold today
							</span>
						)}
					</div>
				)}

				{/* Product Name */}
				<Link href={`/product/${slug}`}>
					<h3 className="font-medium text-gray-900 line-clamp-2 hover:text-primary-500 transition-colors min-h-[3rem] text-sm">
						{name}
					</h3>
				</Link>

				{/* Rating */}
				{rating > 0 && (
					<div className="flex items-center gap-1 mt-2">
						<div className="flex">
							{[1, 2, 3, 4, 5].map((star) => (
								<span
									key={star}
									className={star <= rating ? "text-success-500" : "text-gray-300"}
								>
									★
								</span>
							))}
						</div>
						<span className="text-sm text-gray-600">
							{rating.toFixed(1)} ({reviewCount})
						</span>
					</div>
				)}

				{/* Price */}
				<div className="mt-3">
					<div className="flex items-baseline gap-2 flex-wrap">
						<span className="text-xl font-bold text-primary-500 font-mono">
							{formatPrice(price)}
						</span>
						{originalPrice && (
							<span className="text-xs text-gray-400 line-through">
								{formatPrice(originalPrice)}
							</span>
						)}
					</div>

					{installmentPrice && (
						<p className="text-xs text-gray-600 mt-1">
							or <span className="font-semibold">{formatPrice(installmentPrice)}/mo</span> × 3
						</p>
					)}
				</div>

				{/* Delivery Info */}
				{deliveryFee !== undefined && (
					<div className="mt-2 pt-2 border-t border-gray-100">
						<p className="text-xs text-gray-600">
							🚚 Delivery: <span className="font-semibold">{formatPrice(deliveryFee)}</span>
						</p>
					</div>
				)}

				{/* Flash Deal Countdown */}
				{isFlashDeal && flashDealEndsAt && (
					<div className="mt-3 bg-primary-50 rounded-lg p-2">
						<p className="text-xs text-primary-600 font-semibold text-center">
							⏰ Ends in: <FlashDealCountdown endDate={flashDealEndsAt} />
						</p>
					</div>
				)}
			</div>
		</div>
	);
}

// Flash Deal Countdown Component
function FlashDealCountdown({ endDate }: { endDate: Date }) {
	const [timeLeft, setTimeLeft] = useState("");

	useState(() => {
		const interval = setInterval(() => {
			const now = new Date().getTime();
			const distance = endDate.getTime() - now;

			if (distance < 0) {
				setTimeLeft("EXPIRED");
				clearInterval(interval);
				return;
			}

			const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
			const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
			const seconds = Math.floor((distance % (1000 * 60)) / 1000);

			setTimeLeft(`${hours}h ${minutes}m ${seconds}s`);
		}, 1000);

		return () => clearInterval(interval);
	});

	return <span className="font-mono">{timeLeft}</span>;
}
