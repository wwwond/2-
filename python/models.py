# models.py
from sqlalchemy import Column, Integer, String, DateTime, Numeric, Text, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base


class AppUser(Base):
    __tablename__ = 'appUser'

    userId = Column(Integer, primary_key=True)
    userEmail = Column(String(200), nullable=False)
    userPassword = Column(String(100), nullable=False)
    userName = Column(String(50), nullable=False)
    userSex = Column(String(5), nullable=False)
    userBirth = Column(String(20), nullable=False)
    createdAt = Column(DateTime, server_default=func.sysdate(), nullable=False)

    preferences = relationship('UserPreference', back_populates='user', cascade='all, delete-orphan')
    itineraries = relationship('Itinerary', back_populates='user', cascade='all, delete-orphan')


class UserPreference(Base):
    __tablename__ = 'userPreference'

    preferenceId = Column(Integer, primary_key=True)
    userId = Column(Integer, ForeignKey('appUser.userId'), nullable=False)
    prefTheme = Column(String(100), nullable=False)
    prefDuration = Column(String(50), nullable=False)
    prefRegion = Column(String(100), nullable=False)
    prefStay = Column(String(2000))

    user = relationship('AppUser', back_populates='preferences')
    itineraries = relationship('Itinerary', back_populates='preference', cascade='all, delete-orphan')


class Itinerary(Base):
    __tablename__ = 'itinerary'

    itineraryId = Column('ITINERARYID', Integer, primary_key=True)
    preferenceId = Column('PREFERENCEID', Integer, ForeignKey('userPreference.preferenceId'), nullable=False)
    userId = Column('USERID', Integer, ForeignKey('appUser.userId'), nullable=False)
    startDate = Column('STARTDATE', DateTime, nullable=False)
    endDate = Column('ENDDATE', DateTime, nullable=False)
    createdAt = Column('CREATEDAT', DateTime, server_default=func.sysdate(), nullable=False)
    isDeleted = Column('ISDELETED', Boolean, server_default='0', nullable=False)

    user = relationship('AppUser', back_populates='itineraries')
    preference = relationship('UserPreference', back_populates='itineraries')
    slots = relationship('ScheduleSlot', back_populates='itinerary', cascade='all, delete-orphan')


class Place(Base):
    __tablename__ = 'place'

    placeId = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    theme = Column(String(80), nullable=False)
    avgRating = Column(Numeric(3, 2))
    address = Column(String(200), nullable=False)
    latitude = Column(Numeric(9, 6), nullable=False)
    longitude = Column(Numeric(9, 6), nullable=False)
    description = Column(Text)
    heritageType = Column(String(50))
    infoCenter = Column(Text)
    closedDay = Column(Text)
    experienceInfo = Column(Text)
    minAge = Column(Text)
    businessHours = Column(Text)
    parkingInfo = Column(Text)
    details = Column(Text)
    image = Column(String(2000))

    slots = relationship('ScheduleSlot', back_populates='place', cascade='all, delete-orphan')


class ScheduleSlot(Base):
    __tablename__ = 'scheduleSlot'

    slotId = Column(Integer, primary_key=True)
    itineraryId = Column(Integer, ForeignKey('itinerary.ITINERARYID'), nullable=False)
    placeId = Column(Integer, ForeignKey('place.placeId'), nullable=False)
    travelDate = Column(DateTime, nullable=False)

    itinerary = relationship('Itinerary', back_populates='slots')
    place = relationship('Place', back_populates='slots')
