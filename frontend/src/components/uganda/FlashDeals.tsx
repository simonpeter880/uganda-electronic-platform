"use client";

import { useState, useEffect } from "react";
import ProductCard from "./ProductCard";
import { Zap, ChevronLeft, ChevronRight } from "lucide-react";

interface FlashDealsProps {
	products: Array<{
		id: string;
		name: string;
		slug: string;
		price: number;
		originalPrice: number;
		image: string;
		rating?: number;
		reviewCount?: number;
		stockCount?: number;
		soldToday?: number;
		deliveryFee?: number;
	}>;
	endsAt: Date;
}

export default function FlashDeals({ products, endsAt }: FlashDealsProps) {
	const [timeLeft, setTimeLeft] = useState({ hours: 0, minutes: 0, seconds: 0 });
	const [currentIndex, setCurrentIndex] = useState(0);

	// Countdown timer
	useEffect(() => {
		const interval = setInterval(() => {
			const now = new Date().getTime();
			const distance = endsAt.getTime() - now;

			if (distance < 0) {
				clearInterval(interval);
				setTimeLeft({ hours: 0, minutes: 0, seconds: 0 });
				return;
			}

			const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
			const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
			const seconds = Math.floor((distance % (1000 * 60)) / 1000);

			setTimeLeft({ hours, minutes, seconds });
		}, 1000);

		return () => clearInterval(interval);
	}, [endsAt]);

	// Auto-scroll
	useEffect(() => {
		const autoScroll = setInterval(() => {
			setCurrentIndex((prev) => (prev + 1) % Math.max(1, products.length - 3));
		}, 5000);

		return () => clearInterval(autoScroll);
	}, [products.length]);

	const handlePrev = () => {
		setCurrentIndex((prev) => Math.max(0, prev - 1));
	};

	const handleNext = () => {
		setCurrentIndex((prev) => Math.min(products.length - 4, prev + 1));
	};

	const progress = products.length > 0 ? ((products.filter((p) => p.soldToday && p.soldToday > 0).length) / products.length) * 100 : 0;

	return (
		<section className="bg-gradient-to-br from-primary-500 to-accent-600 rounded-2xl p-6 md:p-8 shadow-lg">
			{/* Header */}
			<div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
				<div className="flex items-center gap-3">
					<div className="w-12 h-12 bg-white rounded-full flex items-center justify-center animate-bounce-slow">
						<Zap size={28} className="text-primary-500" />
					</div>
					<div>
						<h2 className="text-2xl font-bold text-white">Flash Deals</h2>
						<p className="text-white/90 text-sm">Limited time offers - Grab them fast!</p>
					</div>
				</div>

				{/* Countdown Timer */}
				<div className="flex items-center gap-2">
					<span className="text-white/90 text-sm font-medium">Ends in:</span>
					<div className="flex gap-1">
						<TimeBox value={timeLeft.hours} label="H" />
						<span className="text-white text-2xl font-bold">:</span>
						<TimeBox value={timeLeft.minutes} label="M" />
						<span className="text-white text-2xl font-bold">:</span>
						<TimeBox value={timeLeft.seconds} label="S" />
					</div>
				</div>
			</div>

			{/* Progress Bar */}
			<div className="mb-6">
				<div className="flex justify-between text-white/90 text-sm mb-2">
					<span>🔥 Selling Fast!</span>
					<span>{Math.round(progress)}% Claimed</span>
				</div>
				<div className="w-full h-3 bg-white/20 rounded-full overflow-hidden">
					<div
						className="h-full bg-white rounded-full transition-all duration-500 animate-pulse-slow"
						style={{ width: `${progress}%` }}
					/>
				</div>
			</div>

			{/* Products Carousel */}
			<div className="relative">
				{/* Navigation Buttons */}
				{products.length > 4 && (
					<>
						<button
							onClick={handlePrev}
							disabled={currentIndex === 0}
							className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-1/2 z-10 w-12 h-12 bg-white rounded-full shadow-lg flex items-center justify-center hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
							aria-label="Previous"
						>
							<ChevronLeft size={24} className="text-gray-900" />
						</button>
						<button
							onClick={handleNext}
							disabled={currentIndex >= products.length - 4}
							className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-1/2 z-10 w-12 h-12 bg-white rounded-full shadow-lg flex items-center justify-center hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
							aria-label="Next"
						>
							<ChevronRight size={24} className="text-gray-900" />
						</button>
					</>
				)}

				{/* Products Grid */}
				<div className="overflow-hidden">
					<div
						className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 transition-transform duration-500"
						style={{
							transform: `translateX(-${currentIndex * (100 / 4)}%)`,
						}}
					>
						{products.map((product) => (
							<ProductCard
								key={product.id}
								{...product}
								isFlashDeal={true}
								flashDealEndsAt={endsAt}
								installmentPrice={product.price / 3}
							/>
						))}
					</div>
				</div>
			</div>

			{/* Footer CTA */}
			<div className="mt-6 text-center">
				<button className="bg-white text-primary-500 px-8 py-3 rounded-full font-bold hover:bg-gray-50 transition-colors inline-flex items-center gap-2 shadow-md">
					<Zap size={20} />
					View All Flash Deals
				</button>
			</div>
		</section>
	);
}

// Time Box Component
function TimeBox({ value, label }: { value: number; label: string }) {
	return (
		<div className="bg-white/10 backdrop-blur-sm rounded-lg px-2 py-1 min-w-[3rem] text-center">
			<div className="text-2xl font-bold text-white font-mono">
				{value.toString().padStart(2, "0")}
			</div>
			<div className="text-xs text-white/80">{label}</div>
		</div>
	);
}
